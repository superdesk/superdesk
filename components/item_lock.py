from models.item import ItemModel
from models.base_model import ETAG
from superdesk import SuperdeskError


LOCK_USER = 'lock_user'
STATUS = '_status'


class ItemLock():
    def __init__(self, data_layer):
        self.data_layer = data_layer

    def lock(self, filter, user, etag):
        item_model = ItemModel(self.data_layer)
        item = item_model.find_one(filter)
        if item and self._can_lock(item, user):
            # filter[ETAG] = etag
            updates = {LOCK_USER: user}
            item_model.update(filter, updates)
            item[LOCK_USER] = user
        else:
            raise SuperdeskError('Item locked by another user')
        return item

    def unlock(self, filter, user, etag):
        item_model = ItemModel()
        filter[LOCK_USER] = user
        filter[ETAG] = etag
        item = item_model.find_one(filter)
        if item:
            update = {LOCK_USER: None}
            item_model.update(filter, update)

    def _can_lock(self, item, user):
        # TODO: implement
        return True
