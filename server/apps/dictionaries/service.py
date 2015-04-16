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
from flask import request, json
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError
from superdesk import get_resource_service
from apps.dictionaries.resource import DICTIONARY_FILE
from eve import ETAG


logger = logging.getLogger(__name__)


def words(text):
    return re.findall('[a-z]+', text.lower())


def read(stream):
    return stream.read().decode('utf-8')


def merge(doc, words):
    doc['content'] = list(set(doc.get('content', []) + words))


def read_from_file(doc):
    content = doc.pop(DICTIONARY_FILE)
    if 'text/' not in content.mimetype:
        raise SuperdeskApiError.badRequestError('A text dictionary file is required')
    return words(read(content))


class DictionaryService(BaseService):
    def on_create(self, docs):
        for doc in docs:
            if doc.get(DICTIONARY_FILE):
                words = read_from_file(doc)
                merge(doc, words)

    def on_created(self, docs):
        for doc in docs:
            del doc['content']

    def on_update(self, updates, original):
        # parse json list
        if updates.get('content_list'):
            updates['content'] = json.loads(updates.pop('content_list'))

        if not updates.get('content'):
            # append to existing content when uploading without other changes
            updates['content'] = original.get('content', [])

        if updates.get(DICTIONARY_FILE):
            words = read_from_file(updates)
            merge(updates, words)

        if updates.get('content'):
            updates['content'] = sorted(updates.get('content'))


class DictionaryAddWordService(BaseService):

    def create(self, docs, **kwargs):
        dict_id = request.view_args['dict_id']
        dict_service = get_resource_service('dictionaries')
        dictionary = dict_service.find_one(req=None, _id=dict_id)
        if not dictionary:
            raise SuperdeskApiError.notFoundError('Invalid dictionary identifier: ' + dict_id)
        for doc in docs:
            if 'word' in doc:
                dictionary['content'].append(doc['word'])
                dictionary['content'] = sorted(dictionary['content'])
                dict_service.put(dictionary['_id'], dictionary)
                doc[ETAG] = dictionary[ETAG]
        return [dict_id]
