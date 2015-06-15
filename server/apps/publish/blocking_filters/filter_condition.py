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
        },
        'mongo_translation': {
            'type': 'string',
            'nullable': True
        },
        'elastic_translation': {
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



class FilterConditionService(BaseService):
    def on_create(self, docs):
        for doc in docs:
            doc['mongo_translation'] = self._translate_to_mongo_query(doc)

    def _translate_to_mongo_query(self, doc):
        field = doc['field']
        operator = self._get_mongo_operator(doc['operator'])
        value = self._get_mongo_value(doc['operator'], doc['value'])
        doc['mongo_translation'] = {field: {operator: value}}

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
            if value.find(',') > 0:
                return [int(x) for x in value.split(',') if x.strip().isdigit()]
            else:
                return [value]

    def _translate_to_elastic_query(self, doc):
        operator = self._get_elastic_operator(doc['operator'])
        value = self._get_elastic_value(doc, doc['operator'], doc['value'])
        doc['elastic_translation'] = {operator: {doc['field']: value}}

    def _get_elastic_operator(self, operator):
        if operator in ['in', 'nin']:
            return 'terms'
        else:
            return 'query_string'

    def _get_elastic_value(self, doc, operator, value):
        if operator in ['in', 'nin']:
            if value.find(',') > 0:
                value = [int(x) for x in value.split(',') if x.strip().isdigit()]
            else:
                value = [value]
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


