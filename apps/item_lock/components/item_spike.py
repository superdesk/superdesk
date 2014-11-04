from ..models.item import ItemModel
from .item_lock import can_lock
from superdesk import SuperdeskError
from superdesk.utc import utcnow
from superdesk.notification import push_notification
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
import superdesk


IS_SPIKED = 'is_spiked'
EXPIRY = 'expiry'


class ItemSpike(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'item_spike'

    def spike(self, filter, user):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if item and can_lock(item, user):
            updates = {IS_SPIKED: True, EXPIRY: utcnow() + 4}
            item_model.update(filter, updates)
            push_notification('item:spike', item=str(item.get('_id')), user=str(user))
        else:
            raise SuperdeskError("Item couldn't be spiked. It is locked by another user")
        return

    def unspike(self, filter, user):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if item:
            updates = {IS_SPIKED: None, EXPIRY: None}
            item_model.update(filter, updates)
            push_notification('item:unspike', item=str(filter.get('_id')), user=str(user))
