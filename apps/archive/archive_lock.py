from flask import request
from superdesk.resource import Resource
from apps.item_lock.components.item_lock import ItemLock
from .common import get_user, item_url
from apps.common.components.utils import get_component
from superdesk.services import BaseService


class ArchiveLockResource(Resource):
    endpoint_name = 'archive_lock'
    url = 'archive/<{0}:item_id>/lock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'backend': 'custom'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name


class ArchiveLockService(BaseService):

    def on_create(self, docs):
        docs.clear()
        user = get_user(required=True)
        c = get_component(ItemLock)
        c.lock({'_id': request.view_args['item_id']}, user['_id'], None)


class ArchiveUnlockResource(Resource):
    endpoint_name = 'archive_unlock'
    url = 'archive/<{0}:item_id>/unlock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'backend': 'custom'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name


class ArchiveUnlockService(BaseService):

    def on_create(self, docs):
        docs.clear()
        user = get_user(required=True)
        c = get_component(ItemLock)
        c.unlock({'_id': request.view_args['item_id']}, user['_id'], None)
