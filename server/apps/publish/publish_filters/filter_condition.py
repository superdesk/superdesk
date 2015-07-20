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
from superdesk.io.subjectcodes import get_subjectcodeitems

logger = logging.getLogger(__name__)


class FilterConditionResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'nullable': False,
            'iunique': True
        },
        'field': {
            'type': 'string',
            'nullable': False,
            'allowed': ['anpa_category',
                        'urgency',
                        'keywords',
                        'priority',
                        'slugline',
                        'type',
                        'source',
                        'headline',
                        'body_html',
                        'genre',
                        'subject'],
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
        self._check_parameters(docs)

    def on_update(self, updates, original):
        doc = dict(original)
        doc.update(updates)
        self._check_equals([doc])
        self._check_parameters([doc])

    def delete(self, lookup):
        referenced_filters = self._get_referenced_filter_conditions(lookup.get('_id'))
        if referenced_filters.count() > 0:
            references = ','.join([pf['name'] for pf in referenced_filters])
            raise SuperdeskApiError.badRequestError('Filter condition has been referenced in pf:{}'.format(references))
        return super().delete(lookup)

    def _get_referenced_filter_conditions(self, id):
        lookup = {'publish_filter.expression.fc': [id]}
        publish_filters = get_resource_service('publish_filters').get(req=None, lookup=lookup)
        return publish_filters

    def _check_parameters(self, docs):
        parameters = get_resource_service('filter_condition_parameters').get(req=None, lookup=None)
        for doc in docs:
            parameter = [p for p in parameters if p['field'] == doc['field']]
            if not parameter or len(parameter) == 0:
                raise SuperdeskApiError.badRequestError(
                    'Filter condition:{} has unidentified field: {}'
                    .format(doc['name'], doc['field']))
            if doc['operator'] not in parameter[0]['operators']:
                raise SuperdeskApiError.badRequestError(
                    'Filter condition:{} has unidentified operator: {}'
                    .format(doc['name'], doc['operator']))

    def _check_equals(self, docs):
        """
        Checks if any of the filter conditions in the docs
        already exists
        :param docs: List of filter conditions to be tested
        :raises SuperdeskApiError: if any of the filter conditions in the docs
        already exists
        """
        for doc in docs:
            existing_docs = self.get(None, {'field': doc['field'], 'operator': doc['operator']})
            for existing_doc in existing_docs:
                if '_id' in doc and doc['_id'] == existing_doc['_id']:
                    continue
                if self._are_equal(doc, existing_doc):
                    raise SuperdeskApiError.badRequestError(
                        'Filter condition:{} has identical settings'.format(existing_doc['name']))

    def _check_similar(self, filter_condition):
        """
        Checks if the given filter condition already exists (for text fields like headline) or
        if there's any other filter condition that contains the given filter
        condition (for controlled vocabulary fields like urgency).
        For example: if filter_condition ['urgency' in 3,4] exists and if
        filter condition ['urgency' in 3] is searched we'll have a match
        :param filter_condition: Filter conditions to be tested
        :return: Returns the list of matching filter conditions
        """
        parameters = get_resource_service('filter_condition_parameters').get(req=None, lookup=None)
        parameter = [p for p in parameters if p['field'] == filter_condition['field']]
        if parameter[0]['operators'] == ['in', 'nin']:
            # this is a controlled vocabulary field so find the overlapping values
            existing_docs = list(self.get(None,
                                          {'field': filter_condition['field'],
                                           'operator': filter_condition['operator'],
                                           'value': {'$regex': re.compile('.*{}.*'.format(filter_condition['value']),
                                                                          re.IGNORECASE)}}))
            parameter[0]['operators'].remove(filter_condition['operator'])
            existing_docs.extend(list(self.get(None,
                                               {'field': filter_condition['field'],
                                                'operator': parameter[0]['operators'][0],
                                                'value': {'$not': re.compile('.*{}.*'.format(filter_condition['value']),
                                                                             re.IGNORECASE)}})))
        else:
            # find the exact matches
            existing_docs = list(self.get(None, {'field': filter_condition['field'],
                                                 'operator': filter_condition['operator'],
                                                 'value': filter_condition['value']}))
        return existing_docs

    def _are_equal(self, fc1, fc2):
        def get_comparer(fc):
            return ''.join(sorted(fc['value'].upper()))

        return all([fc1['field'] == fc2['field'],
                    fc1['operator'] == fc2['operator'],
                    get_comparer(fc1) == get_comparer(fc2)])

    def get_mongo_query(self, doc):
        field = self._get_field(doc['field'])
        operator = self._get_mongo_operator(doc['operator'])
        value = self._get_mongo_value(doc['operator'], doc['value'], doc['field'])
        return {field: {operator: value}}

    def _get_mongo_operator(self, operator):
        if operator in ['like', 'startswith', 'endswith']:
            return '$regex'
        elif operator == 'notlike':
            return '$not'
        else:
            return '${}'.format(operator)

    def _get_value(self, value, field):
        t = self._get_type(field)
        if value.find(',') > 0:
            return [t(x) for x in value.strip().split(',')]
        return [t(value)]

    def _get_type(self, field):
        if field == 'urgency':
            return int
        else:
            return str

    def _get_mongo_value(self, operator, value, field):
        if operator == 'startswith':
            return re.compile('^{}'.format(value), re.IGNORECASE)
        elif operator == 'like' or operator == 'notlike':
            return re.compile('.*{}.*'.format(value), re.IGNORECASE)
        elif operator == 'endswith':
            return re.compile('.*{}'.format(value), re.IGNORECASE)
        else:
            return self._get_value(value, field)

    def get_elastic_query(self, doc):
        operator = self._get_elastic_operator(doc['operator'])
        value = self._get_elastic_value(doc, doc['operator'], doc['value'], doc['field'])
        field = self._get_field(doc['field'])
        return {operator: {field: value}}

    def _get_elastic_operator(self, operator):
        if operator in ['in', 'nin']:
            return 'terms'
        else:
            return 'query_string'

    def _get_elastic_value(self, doc, operator, value, field):
        if operator in ['in', 'nin']:
            value = self._get_value(value, field)
        elif operator in ['like', 'notlike']:
            value = '{}:*{}*'.format(field, value)
            doc['field'] = 'query'
        elif operator == 'startswith':
            value = '{}:{}*'.format(field, value)
            doc['field'] = 'query'
        elif operator == 'endswith':
            value = '{}:*{}'.format(field, value)
            doc['field'] = 'query'
        return value

    def _get_field(self, field):
        if field == 'anpa_category':
            return 'anpa_category.value'
        elif field == 'genre':
            return 'genre.name'
        elif field == 'subject':
            return 'subject.qcode'
        else:
            return field

    def does_match(self, filter_condition, article):
        field = filter_condition['field']
        operator = filter_condition['operator']
        filter_value = filter_condition['value']

        if field not in article:
            if operator in ['nin', 'notlike']:
                return True
            else:
                return False

        article_value = self._get_field_value(field, article)
        filter_value = self._get_mongo_value(operator, filter_value, field)
        return self._run_filter(article_value, operator, filter_value)

    def _get_field_value(self, field, article):
        if field == 'anpa_category':
            return [c['qcode'] for c in article[field]]
        elif field == 'genre':
            return [g['name'] for g in article[field]]
        elif field == 'subject':
            return [s['qcode'] for s in article[field]]
        else:
            return article[field]

    def _run_filter(self, article_value, operator, filter_value):
        if operator == 'in':
            if isinstance(article_value, list):
                return any([v in filter_value for v in article_value])
            else:
                return article_value in filter_value
        if operator == 'nin':
            if isinstance(article_value, list):
                return all([v not in filter_value for v in article_value])
            else:
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
        return ListCursor([{'field': 'anpa_category',
                            'operators': ['in', 'nin'],
                            'values': values['anpa_category'],
                            'value_field': 'qcode'
                            },
                           {'field': 'urgency',
                            'operators': ['in', 'nin'],
                            'values': values['urgency'],
                            'value_field': 'value'
                            },
                           {'field': 'genre',
                            'operators': ['in', 'nin'],
                            'values': values['genre'],
                            'value_field': 'value'
                            },
                           {'field': 'subject',
                            'operators': ['in', 'nin'],
                            'values': values['subject'],
                            'value_field': 'qcode'
                            },
                           {'field': 'priority',
                            'operators': ['in', 'nin'],
                            'values': values['priority'],
                            'value_field': 'qcode'
                            },
                           {'field': 'keywords',
                            'operators': ['in', 'nin', 'like', 'notlike', 'startswith', 'endswith']
                            },
                           {'field': 'slugline',
                            'operators': ['in', 'nin', 'like', 'notlike', 'startswith', 'endswith']
                            },
                           {'field': 'type',
                            'operators': ['in', 'nin'],
                            'values': values['type'],
                            'value_field': 'value'
                            },
                           {'field': 'source',
                            'operators': ['in', 'nin', 'like', 'notlike', 'startswith', 'endswith']
                            },
                           {'field': 'headline',
                            'operators': ['in', 'nin', 'like', 'notlike', 'startswith', 'endswith']
                            },
                           {'field': 'body_html',
                            'operators': ['in', 'nin', 'like', 'notlike', 'startswith', 'endswith']
                            }])

    def _get_field_values(self):
        values = {}
        values['anpa_category'] = get_resource_service('vocabularies').find_one(req=None, _id='categories')['items']
        values['genre'] = get_resource_service('vocabularies').find_one(req=None, _id='genre')['items']
        values['urgency'] = get_resource_service('vocabularies').find_one(req=None, _id='newsvalue')['items']
        values['priority'] = get_resource_service('vocabularies').find_one(req=None, _id='priority')['items']
        values['type'] = get_resource_service('vocabularies').find_one(req=None, _id='type')['items']
        values['subject'] = get_subjectcodeitems()
        return values
