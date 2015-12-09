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

from apps.search_providers import allowed_search_providers
from superdesk.resource import Resource
from superdesk.utils import required_string

logger = logging.getLogger(__name__)


class SearchProviderResource(Resource):
    schema = {
        'search_provider': {
            'type': 'string',
            'required': True,
            'unique': True,
            'allowed': allowed_search_providers
        },
        'source': required_string,
        'is_closed': {
            'type': 'boolean',
            'default': False
        },
        'last_item_update': {'type': 'datetime'},
        'config': {
            'type': 'dict'
        }
    }

    etag_ignore_fields = ['last_item_update']

    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH', 'DELETE']

    privileges = {'POST': 'search_providers', 'PATCH': 'search_providers', 'DELETE': 'search_providers'}
