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
            doc['mongo_translation'] = self.translate_to_mongo(doc)

    def translate_to_mongo(self, doc):
        field = doc['field']
        operator = self.get_operator(doc['operator'])
        value = self.get_value(doc['operator'], doc['value'])
        doc['mongo_translation'] = {field: {operator: value}}

    def get_operator(self, operator):
        if operator in ['like', 'startswith', 'endswith']:
            return '$regex'
        elif operator == 'notlike':
            return '$not'
        else:
            return '${}'.format(operator)

    def get_value(self, operator, value):
        if operator == 'startswith':
            return '/^{}/i'.format(value)
        elif operator == 'like' or operator == 'notlike':
            return '.*{}.*'.format(value)
        elif operator == 'endswith':
            return '/.*{}/i'.format(value)
        else:
            if value.find(',') > 0:
                return [int(x) for x in value.split(',') if x.strip().isdigit()]
            else:
                return [value]