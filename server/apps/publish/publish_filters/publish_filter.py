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
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'fc': Resource.rel('filter_condition', True),
                        'pf': Resource.rel('publish_filter', True)
                    }
                }
            }
        },
        'name': {
            'type': 'string',
            'nullable': False,
        }
    }

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'name'
    }

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'publish_filters', 'PATCH': 'publish_filters'}


class PublishFilterService(BaseService):
    def build_mongo_query(self, doc):
        filter_condition_service = get_resource_service('filter_condition')
        expressions = []
        for expression in doc.get('publish_filter', []):
            filter_conditions = []
            for filter_dict in expression:
                if 'fc' in filter_dict:
                    current_filter = filter_condition_service.find_one(req=None, _id=filter_dict['fc'])
                    mongo_query = filter_condition_service.get_mongo_query(current_filter)
                else:
                    current_filter = super().find_one(req=None, _id=filter_dict['pf'])
                    mongo_query = self.build_mongo_query(current_filter)
                filter_conditions.append(mongo_query)

            if len(filter_conditions) > 1:
                expressions.append({'$and': filter_conditions})
            else:
                expressions.extend(filter_conditions)

        if len(expressions) > 1:
            return {'$or': expressions}
        else:
            return expressions[0]

    def build_elastic_query(self, doc):
        return {'query': {'filtered': {'query': {'bool': self._get_elastic_query(doc)}}}}

    def _get_elastic_query(self, doc):
        expressions = {'should': []}
        filter_condition_service = get_resource_service('filter_condition')
        for expression in doc.get('publish_filter', []):
            filter_conditions = {'must': []}
            for filter_dict in expression:
                if 'fc' in filter_dict:
                    current_filter = filter_condition_service.find_one(req=None, _id=filter_dict['fc'])
                    elastic_query = filter_condition_service.get_elastic_query(current_filter)
                else:
                    current_filter = super().find_one(req=None, _id=filter_dict['pf'])
                    elastic_query = self._get_elastic_query(current_filter)
                filter_conditions['must'].append(elastic_query)
            expressions['should'].append({'bool': filter_conditions})
        return {'bool': expressions}

    def does_match(self, publish_filter, article):
        filter_condition_service = get_resource_service('filter_condition')
        expressions = []
        for expression in publish_filter.get('publish_filter', []):
            filter_conditions = []
            for filter_dict in expression:
                if 'fc' in filter_dict:
                    filter_condition = filter_condition_service.find_one(req=None, _id=filter_dict['fc'])
                    filter_conditions.append(filter_condition_service.does_match(filter_condition, article))
                else:
                    current_filter = super().find_one(req=None, _id=filter_dict['pf'])
                    filter_conditions.append(self.does_match(current_filter, article))
            expressions.append(all(filter_conditions))
        return any(expressions)
