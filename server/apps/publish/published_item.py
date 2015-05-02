# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk.resource import Resource
from superdesk.services import BaseService
from apps.content import metadata_schema, not_analyzed
from eve.utils import ParsedRequest
from bson.objectid import ObjectId
from superdesk.utc import utcnow
import json

logger = logging.getLogger(__name__)


class PublishedItemResource(Resource):

    datasource = {
        'search_backend': 'elastic',
        'elastic_filter': {'terms': {'state': ['scheduled', 'published', 'killed', 'corrected']}},
        'default_sort': [('_updated', -1)]
    }

    schema = {
        'item_id': {
            'type': 'string',
            'mapping': not_analyzed
        },
        'last_publish_action': {'type': 'string'}
    }

    schema.update(metadata_schema)
    etag_ignore_fields = ['_id', 'last_publish_action', 'highlights', 'item_id']
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}


class PublishedItemService(BaseService):

    def on_create(self, docs):
        # the same content can be published more than once
        # so it is necessary to have a new _id and preserve the original
        for doc in docs:
            doc['item_id'] = doc['_id']
            doc['_created'] = utcnow()
            del doc['_id']

    def get(self, req, lookup):
        # convert to the original _id so everything else works
        items = super().get(req, lookup)
        for item in items:
            item['_id'] = item['item_id']
        return items

    def get_other_published_items(self, _id):
        try:
            query = {'query': {'filtered': {'filter': {'term': {'item_id': _id}}}}}
            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            return super().get(req=request, lookup=None)
        except:
            return []

    def update_other_published_items(self, _id, state):
        items = self.get_other_published_items(_id)
        for item in items:
            super().system_update(ObjectId(item['_id']), {'last_publish_action': state}, item)

    def delete_by_article_id(self, _id):
        lookup = {'query': {'term': {'item_id': _id}}}
        self.delete(lookup=lookup)