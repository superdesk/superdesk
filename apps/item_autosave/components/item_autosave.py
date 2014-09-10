from superdesk import SuperdeskError
from ..models.item_autosave import ItemAutosaveModel
from ...common.components.base_component import BaseComponent
from ...common.models.utils import get_model
from ...item_lock.models.item import ItemModel


class ItemAutosave(BaseComponent):
    def __init__(self, app):
        self.app = app
        self.app.on_item_locked += self.on_item_locked

    @classmethod
    def name(cls):
        return 'archive_autosave'

    def autosave(self, item_id, updates, user, etag):
        item_model = get_model(ItemModel)
        item = item_model.find_one({'_id': item_id})
        if item is None:
            raise SuperdeskError('Invalid item identifier', 404)

        lock_user = item.get('lock_user', None)
        if lock_user and str(lock_user) != str(user['_id']):
            raise SuperdeskError(payload='The item was locked by another user')

        # TODO: implement etag check

        autosave_model = get_model(ItemAutosaveModel)
        item.update(updates)
        self.app.on_item_autosave(item)
        try:
            autosave_model.create(item)
        except:
            id = item['_id']
            del item['_id']
            autosave_model.update({'_id': item_id}, item)
            item['_id'] = id
        self.app.on_item_autosaved(item)
        updates.update(item)
        return updates

    def clear(self, item_id):
        autosave_model = get_model(ItemAutosaveModel)
        return autosave_model.delete({'_id': item_id})

    def on_item_locked(self, item, user):
        self.clear(item['_id'])
