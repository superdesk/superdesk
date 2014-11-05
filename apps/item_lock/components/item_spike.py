from ..models.item import ItemModel
from .item_lock import can_lock
from superdesk import SuperdeskError
from superdesk.utc import get_expiry_date
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
			# for now setting the expiry to next hour
            updates = {IS_SPIKED: True, EXPIRY: get_expiry_date(60)}
            item_model.update(filter, updates)
            push_notification('item:spike', item=str(item.get('_id')), user=str(user))
        else:
            raise SuperdeskError("Item couldn't be spiked. It is locked by another user")
        item = item_model.find_one(filter)
        return item

    def unspike(self, filter, user):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if item:
            updates = {IS_SPIKED: None, EXPIRY: None}
            item_model.update(filter, updates)
            push_notification('item:unspike', item=str(filter.get('_id')), user=str(user))
