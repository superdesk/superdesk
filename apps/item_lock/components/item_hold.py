from ..models.item import ItemModel
from .item_lock import can_lock
from superdesk.notification import push_notification
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
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

    def hold(self, filter, user):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if item and can_lock(item, user):
            updates = {'state': 'on-hold'}
            item_model.update(filter, updates)
            push_notification('item:hold', item=str(item.get('_id')), user=str(user))
        else:
            raise SuperdeskApiError.forbiddenError("Item couldn't be hold. It is locked by another user")
        item = item_model.find_one(filter)
        return item

    def restore(self, filter, user):
        item_model = get_model(ItemModel)
        item = item_model.find_one(filter)
        if item:
            updates = get_restore_updates(item)
            item_model.update(filter, updates)
            push_notification('item:restore', item=str(filter.get('_id')), user=str(user))
