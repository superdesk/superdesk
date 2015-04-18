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


class PublishQueueResource(Resource):
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
            'type': 'string'
        },
        'transmit_started_at': {
            'type': 'datetime'
        },
        'completed_at': {
            'type': 'datetime'
        },
        'state': {
            'type': 'string',
            'allowed': ['pending', 'in-progress', 'success', 'error'],
            'nullable': False
        },
        'output_channel_id': Resource.rel('output_channels'),
        'subscriber_id': Resource.rel('subscribers'),
        'destination': {
            'type': 'dict',
            'schema': {
                'name': {'type': 'string'},
                'delivery_type': {'type': 'string'},
                'config': {'type': 'dict'}
            }
        },
        'error_message': {
            'type': 'string'
        }
    }

    datasource = {'default_sort': [('_created', 1)]}
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}


class PublishQueueService(BaseService):

    def on_create(self, docs):
        for doc in docs:
            doc['state'] = 'pending'

    def on_update(self, updates, original):
        pass
