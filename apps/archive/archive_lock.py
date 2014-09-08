from superdesk.models import BaseModel
from apps.item_lock.components.item_lock import ItemLock
from apps.item_lock.models.io.eve import Eve
from flask import request
from .common import get_user, item_url


class ArchiveLockModel(BaseModel):
    endpoint_name = 'archive_lock'
    url = 'archive/<{0}:item_id>/lock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'backend': 'custom'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name

    def on_create(self, docs):
        docs.clear()
        user = get_user(required=True)
        c = ItemLock(Eve())
        c.lock({'_id': request.view_args['item_id']}, user['_id'], None)


class ArchiveUnlockModel(BaseModel):
    endpoint_name = 'archive_unlock'
    url = 'archive/<{0}:item_id>/unlock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'backend': 'custom'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name

    def on_create(self, docs):
        docs.clear()
        user = get_user(required=True)
        c = ItemLock(Eve())
        c.unlock({'_id': request.view_args['item_id']}, user['_id'], None)
