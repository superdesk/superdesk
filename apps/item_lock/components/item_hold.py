# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from ..models.item import ItemModel
from superdesk.notification import push_notification
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.common.components.utils import get_component
from .item_lock import ItemLock
from superdesk import app
from superdesk.errors import SuperdeskApiError


def get_restore_updates(doc):
    """Generate changes for a given doc to unspike it.

    :param doc: document to unspike
    """
    updates = {
        'state': doc['previous_state']
    }

    desk_id = doc.get('task', {}).get('desk')
    if desk_id:
        desk = app.data.find_one('desks', None, _id=desk_id)
        updates['task'] = {
            'desk': str(desk_id),
            'stage': str(desk['incoming_stage']) if desk_id else None,
            'user': None
        }

    return updates


class ItemHold(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'item_hold'

    def hold(self, filter, user_id, session):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if not item:
            raise SuperdeskApiError.notFoundError()

        can_user_lock, error_message = get_component(ItemLock).can_lock(item, user_id, session)

        if can_user_lock:
            updates = {'state': 'on-hold'}
            item_model.update(filter, updates)
            push_notification('item:hold', item=str(item.get('_id')), user=str(user_id))
        else:
            raise SuperdeskApiError.forbiddenError(message=error_message)

        item = item_model.find_one(filter)
        return item

    def restore(self, filter, user_id):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if not item:
            raise SuperdeskApiError.notFoundError()

        updates = get_restore_updates(item)
        item_model.update(filter, updates)
        push_notification('item:restore', item=str(filter.get('_id')), user=str(user_id))
