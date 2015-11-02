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
from eve.versioning import resolve_document_version

from flask import current_app as app

import superdesk
from superdesk import get_resource_service, config
from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE
from superdesk.notification import push_notification
from superdesk.services import BaseService
from superdesk.utc import get_expiry_date
from superdesk.metadata.utils import item_url
from .common import get_user, is_assigned_to_a_desk, get_expiry
from superdesk.workflow import is_workflow_state_transition_valid
from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from apps.packages import PackageService, TakesPackageService
from apps.archive.archive_rewrite import ArchiveRewriteService
from apps.archive.common import item_operations, ITEM_OPERATION, \
    is_item_in_package, set_sign_off, insert_into_versions

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
        self._validate_item(original)
        self._validate_take(original)
        self._update_rewrite(original)
        set_sign_off(updates, original=original)

    def _validate_item(self, original):
        """
        Raises an exception if the item is linked in a non-take package, the idea being that you don't whant to
        inadvertently remove thing from packages, this force that to be done as a conscious action.
        :param original:
        :raise: An exception or nothing
        """
        if is_item_in_package(original):
            raise SuperdeskApiError.badRequestError(message="This item is in a package" +
                                                            " it needs to be removed before the item can be spiked")

    def _validate_take(self, original):
        takes_service = TakesPackageService()
        if not takes_service.is_last_takes_package_item(original):
            raise SuperdeskApiError.badRequestError(message="Only last take of the package can be spiked.")

    def _update_rewrite(self, original):
        """ Removes the reference from the rewritten story in published collection """
        rewrite_service = ArchiveRewriteService()
        if original.get('rewrite_of') and original.get('event_id'):
            rewrite_service._clear_rewritten_flag(original.get('event_id'), original[config.ID_FIELD])

    def _removed_refs_from_package(self, item):
        """
        Remove reference from the package of the spiked item
        :param item:
        """
        PackageService().remove_spiked_refs_from_package(item)

    def _spike_broadcast_item(self, item):
        """

        :param item:
        :return:
        """
        broadcast_item = get_resource_service('archive_broadcast').get_broadcast_story_from_master_story(item)
        if broadcast_item:
            try:
                updates = {ITEM_STATE: CONTENT_STATE.SPIKED}
                resolve_document_version(updates, ARCHIVE, 'PATCH', broadcast_item)
                self.patch(broadcast_item.get(config.ID_FIELD), updates)
                insert_into_versions(id_=broadcast_item.get(config.ID_FIELD))
            except:
                raise SuperdeskApiError.badRequestError(message="Failed to spike the related broadcast item.")
        else:
            get_resource_service('archive_broadcast').remove_rewrite_refs(item)

    def update(self, id, updates, original):
        original_state = original[ITEM_STATE]
        if not is_workflow_state_transition_valid('spike', original_state):
            raise InvalidStateTransitionError()

        user = get_user(required=True)

        item = get_resource_service(ARCHIVE).find_one(req=None, _id=id)
        expiry_minutes = app.settings['SPIKE_EXPIRY_MINUTES']

        # check if item is in a desk. If it's then use the desks spike_expiry
        if is_assigned_to_a_desk(item):
            desk = get_resource_service('desks').find_one(_id=item['task']['desk'], req=None)
            expiry_minutes = desk.get('spike_expiry', expiry_minutes)

        updates[EXPIRY] = get_expiry_date(expiry_minutes)
        updates[REVERT_STATE] = item.get(ITEM_STATE, None)

        if original.get('rewrite_of'):
            updates['rewrite_of'] = None

        if original.get('broadcast'):
            updates['broadcast'] = {
                'status': '',
                'master_id': None,
                'takes_package_id': None,
                'rewrite_id': None
            }

        item = self.backend.update(self.datasource, id, updates, original)
        push_notification('item:spike', item=str(item.get(config.ID_FIELD)), user=str(user))
        self._removed_refs_from_package(id)
        self._spike_broadcast_item(original)
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
        set_sign_off(updates, original=original)

    def update(self, id, updates, original):
        original_state = original[ITEM_STATE]
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
    exclude_states=['spiked', 'published', 'scheduled', 'corrected', 'killed'],
    privileges=['spike']
)

superdesk.workflow_action(
    name='unspike',
    include_states=['spiked'],
    privileges=['unspike']
)
