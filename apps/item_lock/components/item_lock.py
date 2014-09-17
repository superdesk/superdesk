from ..models.item import ItemModel
from superdesk import SuperdeskError
from superdesk.utc import utcnow
from superdesk.notification import push_notification
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model


LOCK_USER = 'lock_user'
STATUS = '_status'


class ItemLock(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'item_lock'

    def lock(self, filter, user, etag):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if item and self._can_lock(item, user):
            updates = {LOCK_USER: user, 'lock_time': utcnow()}
            item_model.update(filter, updates)
            item[LOCK_USER] = user
            push_notification('item:lock', item=str(item.get('_id')), user=str(user))
        else:
            raise SuperdeskError('Item locked by another user')
        return item

    def unlock(self, filter, user, etag):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if item:
            self.app.on_item_unlock(item, user)
            updates = {LOCK_USER: None, 'lock_time': None, 'force_unlock': True}
            item_model.update(filter, updates)
            self.app.on_item_unlocked(item, user)
            push_notification('item:unlock', item=str(filter.get('_id')))

    def _can_lock(self, item, user):
        # TODO: implement
        return True
