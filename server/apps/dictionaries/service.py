# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import re
import logging
import collections
from flask import json
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError
from apps.dictionaries.resource import DICTIONARY_FILE


logger = logging.getLogger(__name__)


def encode_dict(words_dict):
    return json.dumps(words_dict)


def decode_dict(words_list):
    return json.loads(words_list)


def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model


def words(text):
    return [w for w in re.findall('[^\W_]+', text.lower()) if not w.isdigit()]


def add_word(words, word, count):
    """Add word with count to words model.

    :param words: words model
    :param word
    :param count
    """
    words.setdefault(word, 0)
    words[word] += count


def add_words(nwords, text, val=1):
    for word in words(text):
        add_word(nwords, word, val)


def read(stream):
    return stream.read().decode('utf-8')


def merge(doc, words):
    doc.setdefault('content', {})
    for word, count in words.items():
        add_word(doc['content'], word, count)


def read_from_file(doc):
    content = doc.pop(DICTIONARY_FILE)
    if 'text/' not in content.mimetype:
        raise SuperdeskApiError.badRequestError('A text dictionary file is required')
    return train(words(read(content)))


class DictionaryService(BaseService):
    def on_create(self, docs):
        for doc in docs:
            if self.find_one(req=None, name=doc['name'], language_id=doc['language_id']):
                raise SuperdeskApiError.badRequestError(message='The dictionary already exists',
                                                        payload={'name': 'duplicate'})
            if doc.get(DICTIONARY_FILE):
                words = read_from_file(doc)
                merge(doc, words)
            if 'content' in doc:
                doc['content'] = encode_dict(doc['content'])

    def on_created(self, docs):
        for doc in docs:
            doc.pop('content', None)

    def on_updated(self, updates, original):
        if 'content' in updates:
            updates['content'] = decode_dict(updates['content'])

    def find_one(self, req, **lookup):
        doc = super().find_one(req, **lookup)
        if doc and 'content' in doc:
            doc['content'] = decode_dict(doc['content'])
        return doc

    def on_fetched(self, result):
        for doc in result['_items']:
            if 'content' in doc:
                doc['content'] = decode_dict(doc['content'])

    def get_model_for_lang(self, lang):
        """Get model for given language.

        It will use all active dictionaries for given language combined.

        :param lang: language code
        """
        model = {}
        lookup = {'$and': [{'language_id': lang}, {'is_active': {'$in': ['true', None]}}]}
        dicts = self.get(req=None, lookup=lookup)
        for _dict in dicts:
            if 'content' in _dict:
                content = decode_dict(_dict['content'])
            else:
                content = {}
            for word, count in content.items():
                add_word(model, word, count)
        return model

    def on_update(self, updates, original):
        # parse json list
        if updates.get('content_list'):
            updates['content'] = json.loads(updates.pop('content_list'))

        # handle manual changes
        nwords = original.get('content', {}).copy()
        for word, val in updates.get('content', {}).items():
            if val:
                add_words(nwords, word, val)
            else:
                nwords.pop(word, None)
        updates['content'] = nwords

        # handle uploaded file
        if updates.get(DICTIONARY_FILE):
            file_words = read_from_file(updates)
            merge(updates, file_words)

        # save it as string, otherwise it would order keys and it takes forever
        if 'content' in updates:
            updates['content'] = encode_dict(updates['content'])
