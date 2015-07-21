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
import superdesk
from cerberus import Validator

logger = logging.getLogger(__name__)


class ValidateResource(superdesk.Resource):
    schema = {
        'act': {'type': 'string', 'required': True},
        'type': {'type': 'string', 'required': True},
        'validate': {
            'type': 'dict',
            'required': True
        }
    }

    resource_methods = ['POST']
    item_methods = []


class ValidateService(superdesk.Service):

    def create(self, docs, **kwargs):
        for doc in docs:
            doc['errors'] = self._validate(doc)

        return [doc['errors'] for doc in docs]

    def _validate(self, doc):
        lookup = {'act': doc['act'], 'type': doc['type']}
        validators = superdesk.get_resource_service('validators').get(req=None, lookup=lookup)
        for validator in validators:
            v = Validator()
            v.allow_unknown = True
            v.validate(doc['validate'], validator['schema'])
            error_list = v.errors
            response = []
            for e in error_list:
                if error_list[e] == 'required field' or type(error_list[e]) is dict:
                    response.append('{} is a required field'.format(e.upper()))
                elif 'min length is' in error_list[e]:
                    response.append('{} is too short'.format(e.upper()))
                elif 'max length is' in error_list[e]:
                    response.append('{} is too long'.format(e.upper()))
                else:
                    response.append('{} {}'.format(e.upper(), error_list[e]))
            return response
        else:
            return ['validator was not found for {}'.format(doc['act'])]
