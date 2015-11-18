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
from superdesk.metadata.item import ITEM_TYPE

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
            doc['errors'] = self._validate(doc, **kwargs)

        return [doc['errors'] for doc in docs]

    def _validate(self, doc, **kwargs):
        lookup = {'act': doc['act'], 'type': doc[ITEM_TYPE]}
        use_headline = kwargs and 'headline' in kwargs
        validators = superdesk.get_resource_service('validators').get(req=None, lookup=lookup)
        for validator in validators:
            v = Validator()
            v.allow_unknown = True
            v.validate(doc['validate'], validator['schema'])
            error_list = v.errors
            response = []
            for e in error_list:
                if error_list[e] == 'required field' or type(error_list[e]) is dict:
                    message = '{} is a required field'.format(e.upper())
                elif 'min length is' in error_list[e]:
                    message = '{} is too short'.format(e.upper())
                elif 'max length is' in error_list[e]:
                    message = '{} is too long'.format(e.upper())
                else:
                    message = '{} {}'.format(e.upper(), error_list[e])

                if use_headline:
                    response.append('{}: {}'.format(doc['validate'].get('headline',
                                                                        doc['validate'].get('_id')), message))
                else:
                    response.append(message)
            return response
        else:
            return ['validator was not found for {}'.format(doc['act'])]
