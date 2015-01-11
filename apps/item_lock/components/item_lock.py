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
from eve.utils import config
from superdesk.errors import SuperdeskApiError
from superdesk.utc import utcnow
from superdesk.notification import push_notification
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
import superdesk


LOCK_USER = 'lock_user'
LOCK_SESSION = 'lock_session'
STATUS = '_status'
TASK = 'task'
USER = 'user'


class ItemLock(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'item_lock'

    def lock(self, filter, user, session, etag):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if not item:
            raise SuperdeskApiError.notFoundError(message="Item not found.")

        can_user_lock, error_message = self.can_lock(item, user, session)

        if can_user_lock:
            self.app.on_item_lock(item, user)
            updates = {LOCK_USER: user, LOCK_SESSION: session, 'lock_time': utcnow()}
            item_model.update(filter, updates)

            if item.get(TASK):
                item[TASK]['user'] = user
            else:
                item[TASK] = {'user': user}

            superdesk.get_resource_service('tasks').assign_user(item[config.ID_FIELD], item[TASK])
            self.app.on_item_locked(item, user)
            push_notification('item:lock', item=str(item.get(config.ID_FIELD)), user=str(user))
        else:
            raise SuperdeskApiError.forbiddenError(error_message)

        item = item_model.find_one(filter)
        return item

    def unlock(self, filter, user, session, etag):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if item:
            self.app.on_item_unlock(item, user)
            updates = {LOCK_USER: None, LOCK_SESSION: None, 'lock_time': None, 'force_unlock': True}
            item_model.update(filter, updates)
            self.app.on_item_unlocked(item, user)
            push_notification('item:unlock', item=str(filter.get(config.ID_FIELD)), user=str(user))
        item = item_model.find_one(filter)
        return item

    def can_lock(self, item, user_id, session_id):
        """
        Function checks whether user can lock the item or not.
        :param item: Content item.
        :param user_id: user id performing the lock.
        :param session_id: session id.
        :return: if can lock then True else (False, 'error message').
        """
        # TODO: modify this function when read only permissions for stages are implemented.
        if item.get(LOCK_USER):
            if item.get(LOCK_USER) == user_id:
                if item.get(LOCK_SESSION) == session_id:
                    return False, 'Item is locked already locked by you.'
                else:
                    return False, 'Item is locked by you in another session.'
            else:
                return False, 'Item is locked by another user.'

        item_location = item.get(TASK)

        if not item_location:
            return True, ''

        if item_location.get('desk'):
            if superdesk.get_resource_service('user_desks').is_member(user_id, item_location.get('desk')):
                return True, ''
            else:
                return False, 'User is not a member of the desk.'
        else:
            if not item_location.get('user', '') == user_id:
                return False, 'Item belongs to another user.'

        return True, ''
