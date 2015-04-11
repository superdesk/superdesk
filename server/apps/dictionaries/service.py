# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from flask import request
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError
from collections import Counter
from superdesk import get_resource_service
from apps.dictionaries.resource import DICTIONARY_FILE
from eve import ETAG


logger = logging.getLogger(__name__)


class DictionaryService(BaseService):
    def on_create(self, docs):
        for doc in docs:
            if doc.get(DICTIONARY_FILE):
                self._read_from_file(doc)

    def on_created(self, docs):
        for doc in docs:
            del doc['content']

    def on_update(self, updates, original):
        if updates.get(DICTIONARY_FILE):
            words = Counter(original['content'])
            self._read_from_file(updates, words)

    def _read_from_file(self, doc, words=Counter()):
        content = doc[DICTIONARY_FILE]
        if 'text/' not in content.mimetype:
            raise SuperdeskApiError.badRequestError('A text dictionary file is required')
        doc['content'] = self._read_from_stream(read_line_from_stream(content), words)
        del doc[DICTIONARY_FILE]

    def _read_from_stream(self, stream, words=Counter()):
        for line in stream:
            line = line.strip()
            if line:
                words[line] += 1
        return sorted(list(words.keys()))


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


def read_line_from_stream(stream):
    while True:
        line = stream.readline()
        if not line:
            raise StopIteration()
        yield line.decode('utf-8').strip()
