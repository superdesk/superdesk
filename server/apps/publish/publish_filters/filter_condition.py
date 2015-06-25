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
import re
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.utils import ListCursor
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError

logger = logging.getLogger(__name__)


class FilterConditionResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'nullable': False,
        },
        'field': {
            'type': 'string',
            'nullable': False,
            'allowed': ['anpa-category',
                        'urgency',
                        'keywords',
                        'priority',
                        'slugline',
                        'type',
                        'source',
                        'headline',
                        'body_html',
                        'genre'],
        },
        'operator': {
            'type': 'string',
            'allowed': ['in',
                        'nin',
                        'like',
                        'notlike',
                        'startswith',
                        'endswith'],
            'nullable': False,
        },
        'value': {
            'type': 'string',
            'nullable': False,
        }
    }

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'name'
    }

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'publish_filters',
                  'PATCH': 'publish_filters',
                  'DELETE': 'publish_filters'}


class FilterConditionService(BaseService):
    def on_create(self, docs):
        self._check_equals(docs)

    def on_update(self, updates, original):
        doc = dict(original)
        doc.update(updates)
        self._check_equals([doc])

    def _check_equals(self, docs):
        for doc in docs:
            existing_docs = self.get(None, {'field': doc['field'], 'operator': doc['operator']})
            for existing_doc in existing_docs:
                if '_id' in doc and doc['_id'] == existing_doc['_id']:
                    continue
                if self._are_equal(doc, existing_doc):
                    raise SuperdeskApiError.badRequestError(
                        'Filter condition:{} has identical settings'.format(existing_doc['name']))

    def _are_equal(self, fc1, fc2):
        def get_comparer(fc):
            return ''.join(sorted(fc['value'].upper()))

        return all([fc1['field'] == fc2['field'],
                    fc1['operator'] == fc2['operator'],
                    get_comparer(fc1) == get_comparer(fc2)])

    def get_mongo_query(self, doc):
        field = doc['field']
        operator = self._get_mongo_operator(doc['operator'])
        value = self._get_mongo_value(doc['operator'], doc['value'])
        return {field: {operator: value}}

    def _get_mongo_operator(self, operator):
        if operator in ['like', 'startswith', 'endswith']:
            return '$regex'
        elif operator == 'notlike':
            return '$not'
        else:
            return '${}'.format(operator)

    def _get_mongo_value(self, operator, value):
        if operator == 'startswith':
            return re.compile('^{}'.format(value), re.IGNORECASE)
        elif operator == 'like' or operator == 'notlike':
            return re.compile('.*{}.*'.format(value), re.IGNORECASE)
        elif operator == 'endswith':
            return re.compile('.*{}'.format(value), re.IGNORECASE)
        else:
            if isinstance(value, str) and value.find(',') > 0:
                if value.split(',')[0].strip().isdigit():
                    return [int(x) for x in value.split(',') if x.strip().isdigit()]
                else:
                    value.split(',')
            else:
                return [value]

    def get_elastic_query(self, doc):
        operator = self._get_elastic_operator(doc['operator'])
        value = self._get_elastic_value(doc, doc['operator'], doc['value'])
        return {operator: {doc['field']: value}}

    def _get_elastic_operator(self, operator):
        if operator in ['in', 'nin']:
            return 'terms'
        else:
            return 'query_string'

    def _get_elastic_value(self, doc, operator, value):
        if operator in ['in', 'nin']:
            if isinstance(value, str) and value.find(',') > 0:
                if value.split(',')[0].strip().isdigit():
                    return [int(x) for x in value.split(',') if x.strip().isdigit()]
                else:
                    value.split(',')
            else:
                return [value]
        elif operator in ['like', 'notlike']:
            value = '{}:*{}*'.format(doc['field'], value)
            doc['field'] = 'query'
        elif operator == 'startswith':
            value = '{}:{}*'.format(doc['field'], value)
            doc['field'] = 'query'
        elif operator == 'endswith':
            value = '{}:*{}'.format(doc['field'], value)
            doc['field'] = 'query'
        return value

    def does_match(self, filter_condition, article):
        field = filter_condition['field']
        operator = filter_condition['operator']
        filter_value = filter_condition['value']

        if field not in article:
            if operator in ['nin', 'notlike']:
                return True
            else:
                return False

        article_value = article[field]
        filter_value = self._get_mongo_value(operator, filter_value)

        if operator == 'in':
            return article_value in filter_value
        if operator == 'nin':
            return article_value not in filter_value
        if operator == 'like' or operator == 'startswith' or operator == 'endswith':
            return filter_value.match(article_value)
        if operator == 'notlike':
            return not filter_value.match(article_value)


class FilterConditionParametersResource(Resource):
    url = "filter_conditions/parameters"
    resource_methods = ['GET']
    item_methods = []


class FilterConditionParametersService(BaseService):
    def get(self, req, lookup):
        values = self._get_field_values()
        return ListCursor([{'field': 'anpa-category',
                            'operators': ['in', 'nin'],
                            'values': values['anpa_category']
                            },
                           {'field': 'urgency',
                            'operators': ['in', 'nin'],
                            'values': values['urgency']
                            },
                           {'field': 'keywords',
                            'operators': ['in', 'nin', 'like', 'notlike', 'startswith', 'endswith']
                            }])

    def _get_field_values(self):
        values = {}
        values['anpa_category'] = get_resource_service('vocabularies').find_one(req=None, _id='categories')['items']
        values['genre'] = get_resource_service('vocabularies').find_one(req=None, _id='genre')['items']
        values['urgency'] = get_resource_service('vocabularies').find_one(req=None, _id='newsvalue')['items']
        return values
