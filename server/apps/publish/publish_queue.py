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
from superdesk import get_resource_service
from superdesk.notification import push_notification
from superdesk.resource import Resource
from superdesk.services import BaseService

logger = logging.getLogger(__name__)


class PublishQueueResource(Resource):
    schema = {
        'item_id': Resource.rel('archive', type='string'),
        'formatted_item_id': Resource.rel('formatted_item', type='string'),
        'transmit_started_at': {
            'type': 'datetime'
        },
        'completed_at': {
            'type': 'datetime'
        },
        'state': {
            'type': 'string',
            'allowed': ['pending', 'in-progress', 'success', 'canceled', 'error'],
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
        'published_seq_num': {
            'type': 'integer'
        },
        'selector_codes': {
            'type': 'list'
        },
        'error_message': {
            'type': 'string'
        },
        'publish_schedule': {
            'type': 'datetime'
        },
        'publishing_action': {
            'type': 'string'
        },
        'unique_name': {
            'type': 'string'
        },
        'content_type': {
            'type': 'string'
        },
        'headline': {
            'type': 'string'
        }
    }

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'item_id'
    }

    datasource = {'default_sort': [('_created', 1)]}
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}


class PublishQueueService(BaseService):

    def on_create(self, docs):
        output_channel_service = get_resource_service('output_channels')

        for doc in docs:
            doc['state'] = 'pending'

            if 'published_seq_num' not in doc:
                output_channel = output_channel_service.find_one(req=None, _id=doc['output_channel_id'])
                doc['published_seq_num'] = output_channel_service.generate_sequence_number(output_channel)

    def on_updated(self, updates, original):
        if updates.get('state', '') != original.get('state', ''):
            push_notification('publish_queue:update',
                              queue_id=str(original['_id']),
                              completed_at=(updates.get('completed_at').isoformat()
                                            if updates.get('completed_at') else None),
                              state=updates.get('state'),
                              error_message=updates.get('error_message')
                              )

    def delete_by_article_id(self, _id):
        lookup = {'item_id': _id}
        self.delete(lookup=lookup)
