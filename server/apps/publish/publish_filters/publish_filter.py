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
from superdesk import get_resource_service
from superdesk.resource import Resource
from superdesk.services import BaseService

logger = logging.getLogger(__name__)


class PublishFilterResource(Resource):
    schema = {
        'publish_filter': {
            'type': 'list',
            'schema': {
                'type': 'list',
                'schema': Resource.rel('filter_condition', True)
            }
        },
        'name': {
            'type': 'string',
            'nullable': False,
        },
        'mongo_query': {
            'type': 'string',
            'nullable': True
        },
        'elastic_query': {
            'type': 'string',
            'nullable': True
        }
    }

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'name'
    }

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}


class PublishFilterService(BaseService):
    def on_create(self, docs):
        for doc in docs:
            doc['mongo_query'] = self._join_mongo_queries(doc)

    def _join_mongo_queries(self, doc):
        expressions = []
        for expression in doc.get('publish_filter', []):
            filter_conditions = []
            for filter_condition_id in expression:
                filter_condition = get_resource_service('filter_condition').find_one(req=None, _id=filter_condition_id)
                filter_conditions.append(filter_condition['mongo_query'])
            expressions.append({'$and': filter_conditions})
        return {'$or': expressions}
