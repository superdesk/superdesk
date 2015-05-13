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
        validator = superdesk.get_resource_service('validators').find_one(req=None, _id=doc['act'])
        if validator:
            v = Validator()
            v.allow_unknown = True
            v.validate(doc['validate'], validator['schema'])
            return v.errors
        else:
            return {doc['act']: 'validator was not found'}
