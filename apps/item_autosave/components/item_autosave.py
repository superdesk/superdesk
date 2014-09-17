import superdesk
from ..models.item_autosave import ItemAutosaveModel
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.item_lock.models.item import ItemModel


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
            raise superdesk.SuperdeskError('Invalid item identifier', 404)
        if etag:
            item_model.validate_etag(item, etag)

        lock_user = item.get('lock_user', None)
        if lock_user and str(lock_user) != str(user['_id']):
            raise superdesk.SuperdeskError(payload='The item was locked by another user')

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
