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

from flask import current_app as app


from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from superdesk.notification import push_notification
from superdesk.services import BaseService
from superdesk.utc import get_expiry_date
from .common import get_user, item_url, is_assigned_to_a_desk
from eve.utils import config
from superdesk.workflow import is_workflow_state_transition_valid
from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from apps.tasks import get_expiry
from apps.packages import PackageService, TakesPackageService
from apps.archive.common import item_operations, ITEM_OPERATION


logger = logging.getLogger(__name__)

EXPIRY = 'expiry'
REVERT_STATE = 'revert_state'
ITEM_SPIKE = 'spike'
ITEM_UNSPIKE = 'unspike'
item_operations.extend([ITEM_SPIKE, ITEM_UNSPIKE])


class ArchiveSpikeResource(ArchiveResource):
    endpoint_name = 'archive_spike'
    resource_title = endpoint_name
    datasource = {'source': ARCHIVE}

    url = "archive/spike"
    item_url = item_url

    resource_methods = []
    item_methods = ['PATCH']

    privileges = {'PATCH': 'spike'}


class ArchiveUnspikeResource(ArchiveResource):
    endpoint_name = 'archive_unspike'
    resource_title = endpoint_name
    datasource = {'source': ARCHIVE}

    url = "archive/unspike"
    item_url = item_url

    resource_methods = []
    item_methods = ['PATCH']

    privileges = {'PATCH': 'unspike'}


class ArchiveSpikeService(BaseService):

    def on_update(self, updates, original):
        updates[ITEM_OPERATION] = ITEM_SPIKE
        takes_service = TakesPackageService()
        if not takes_service.can_spike_takes_package_item(original):
            raise SuperdeskApiError.badRequestError(message="Only last take of the package can be spiked.")

    def update(self, id, updates, original):
        original_state = original[config.CONTENT_STATE]
        if not is_workflow_state_transition_valid('spike', original_state):
            raise InvalidStateTransitionError()

        package_service = PackageService()
        user = get_user(required=True)

        item = get_resource_service(ARCHIVE).find_one(req=None, _id=id)
        expiry_minutes = app.settings['SPIKE_EXPIRY_MINUTES']

        # check if item is in a desk. If it's then use the desks spike_expiry
        if is_assigned_to_a_desk(item):
            desk = get_resource_service('desks').find_one(_id=item['task']['desk'], req=None)
            expiry_minutes = desk.get('spike_expiry', expiry_minutes)

        updates[EXPIRY] = get_expiry_date(expiry_minutes)
        updates[REVERT_STATE] = item.get(app.config['CONTENT_STATE'], None)

        item = self.backend.update(self.datasource, id, updates, original)
        push_notification('item:spike', item=str(item.get('_id')), user=str(user))
        package_service.remove_spiked_refs_from_package(id)
        return item


class ArchiveUnspikeService(BaseService):

    def get_unspike_updates(self, doc):
        """Generate changes for a given doc to unspike it.

        :param doc: document to unspike
        """
        updates = {REVERT_STATE: None, EXPIRY: None, 'state': doc.get(REVERT_STATE),
                   ITEM_OPERATION: ITEM_UNSPIKE}

        desk_id = doc.get('task', {}).get('desk')
        if desk_id:
            desk = app.data.find_one('desks', None, _id=desk_id)
            updates['task'] = {
                'desk': str(desk_id),
                'stage': str(desk['incoming_stage']) if desk_id else None,
                'user': None
            }

        updates['expiry'] = get_expiry(desk_id=desk_id)
        return updates

    def on_update(self, updates, original):
        updates[ITEM_OPERATION] = ITEM_UNSPIKE

    def update(self, id, updates, original):
        original_state = original[config.CONTENT_STATE]
        if not is_workflow_state_transition_valid('unspike', original_state):
            raise InvalidStateTransitionError()
        user = get_user(required=True)

        item = get_resource_service(ARCHIVE).find_one(req=None, _id=id)
        updates.update(self.get_unspike_updates(item))

        self.backend.update(self.datasource, id, updates, original)
        item = get_resource_service(ARCHIVE).find_one(req=None, _id=id)

        push_notification('item:unspike', item=str(id), user=str(user))
        return item


superdesk.workflow_state('spiked')

superdesk.workflow_action(
    name='spike',
    exclude_states=['spiked', 'published', 'scheduled', 'killed'],
    privileges=['spike']
)

superdesk.workflow_action(
    name='unspike',
    include_states=['spiked'],
    privileges=['unspike']
)
