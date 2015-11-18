# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk


class ValidatorsResource(superdesk.Resource):
    schema = {
        '_id': {'type': 'string', 'required': True, 'unique': True},
        'act': {'type': 'string', 'required': True},
        'type': {'type': 'string', 'required': True},
        'schema': {
            'type': 'dict',
            'required': False
        }
    }

    resource_methods = ['POST']
    item_methods = []


class ValidatorsService(superdesk.Service):
    pass
