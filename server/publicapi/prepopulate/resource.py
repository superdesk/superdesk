# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.resource import Resource


prepopulate_schema = {
    'profile': {
        'type': 'string',
        'required': False,
        'default': 'app_prepopulate_data'
    },
    'remove_first': {
        'type': 'boolean',
        'required': False,
        'default': True
    }
}


class PrepopulateResource(Resource):
    """Prepopulate application data."""
    schema = prepopulate_schema
    resource_methods = ['POST']
