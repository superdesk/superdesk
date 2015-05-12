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


class FormattedItemResource(Resource):
    schema = {
        'item_id': Resource.rel('archive', type='string'),
        'item_version': {
            'type': 'string',
            'nullable': False,
        },
        'formatted_item': {
            'type': 'string',
            'nullable': False,
        },
        'format': {
            'type': 'string',
            'nullable': False,
        },
        'published_seq_num': {
            'type': 'integer'
        }
    }

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'item_id'
    }

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}


class FormattedItemService(BaseService):
    pass
