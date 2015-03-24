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
from superdesk.io import allowed_providers
from superdesk.activity import ACTIVITY_CREATE, ACTIVITY_EVENT, ACTIVITY_UPDATE, notify_and_add_activity
from superdesk import get_resource_service
from settings import INGEST_EXPIRY_MINUTES


logger = logging.getLogger(__name__)


class IngestProviderResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'type': {
            'type': 'string',
            'required': True,
            'allowed': allowed_providers
        },
        'content_expiry': {
            'type': 'integer',
            'default': INGEST_EXPIRY_MINUTES
        },
        'config': {
            'type': 'dict'
        },
        'ingested_count': {
            'type': 'integer'
        },
        'accepted_count': {
            'type': 'integer'
        },
        'token': {
            'type': 'dict'
        },
        'source': {
            'type': 'string',
            'required': True,
        },
        'is_closed': {
            'type': 'boolean',
            'default': False
        },
        'update_schedule': {
            'type': 'dict',
            'schema': {
                'hours': {'type': 'integer'},
                'minutes': {'type': 'integer', 'default': 5},
                'seconds': {'type': 'integer'},
            }
        },
        'idle_time': {
            'type': 'dict',
            'schema': {
                'hours': {'type': 'integer'},
                'minutes': {'type': 'integer'},
            }
        },
        'last_updated': {'type': 'datetime'},
        'last_item_update': {'type': 'datetime'},
        'rule_set': Resource.rel('rule_sets', nullable=True),
        'notifications': {
            'type': 'dict',
            'schema': {
                'on_update': {'type': 'boolean', 'default': True},
                'on_close': {'type': 'boolean', 'default': True},
                'on_open': {'type': 'boolean', 'default': True},
                'on_error': {'type': 'boolean', 'default': True}
            }
        },
        'routing_scheme': Resource.rel('routing_schemes', nullable=True)
    }

    item_methods = ['GET', 'PATCH']

    privileges = {'POST': 'ingest_providers', 'PATCH': 'ingest_providers'}


class IngestProviderService(BaseService):
    def __init__(self, datasource=None, backend=None):
        super().__init__(datasource=datasource, backend=backend)
        self.user_service = get_resource_service('users')

    def _get_administrators(self):
        return self.user_service.get_users_by_user_type('administrator')

    def on_create(self, docs):
        for doc in docs:
            if doc.get('content_expiry', 0) == 0:
                doc['content_expiry'] = INGEST_EXPIRY_MINUTES

    def on_created(self, docs):
        for doc in docs:
            notify_and_add_activity(ACTIVITY_CREATE, 'created Ingest Channel {{name}}', item=doc,
                                    user_list=self._get_administrators(),
                                    name=doc.get('name'))

        logger.info("Created Ingest Channel. Data:{}".format(docs))

    def on_update(self, updates, original):
        if updates.get('content_expiry') == 0:
            updates['content_expiry'] = INGEST_EXPIRY_MINUTES

    def on_updated(self, updates, original):

        do_notification = updates.get('notifications', {})\
            .get('on_update', original.get('notifications', {}).get('on_update', True))
        notify_and_add_activity(ACTIVITY_UPDATE, 'updated Ingest Channel {{name}}', item=original,
                                user_list=self._get_administrators()
                                if do_notification else None,
                                name=updates.get('name', original.get('name')))

        if updates.get('is_closed') != original.get('is_closed', False):
            status = ''
            do_notification = False

            if updates.get('is_closed'):
                status = 'closed'
                do_notification = updates.get('notifications', {}). \
                    get('on_close', original.get('notifications', {}).get('on_close', True))
            elif not updates.get('is_closed'):
                status = 'opened'
                do_notification = updates.get('notifications', {}). \
                    get('on_open', original.get('notifications', {}).get('on_open', True))

            notify_and_add_activity(ACTIVITY_EVENT, '{{status}} Ingest Channel {{name}}', item=original,
                                    user_list=self._get_administrators()
                                    if do_notification else None,
                                    name=updates.get('name', original.get('name')),
                                    status=status)

        logger.info("Updated Ingest Channel. Data: {}".format(updates))
