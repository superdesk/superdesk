from flask import request
from superdesk.resource import Resource
from .common import get_user, item_url
from superdesk.services import BaseService
from apps.common.components.utils import get_component
from apps.item_lock.components.item_lock import ItemLock


class ArchiveLockResource(Resource):
    endpoint_name = 'archive_lock'
    url = 'archive/<{0}:item_id>/lock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'source': 'archive'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name


class ArchiveLockService(BaseService):

    def create(self, docs, **kwargs):
        user = get_user(required=True)
        c = get_component(ItemLock)
        item_id = request.view_args['item_id']
        c.lock({'_id': request.view_args['item_id']}, user['_id'], None)
        return [item_id]


class ArchiveUnlockResource(Resource):
    endpoint_name = 'archive_unlock'
    url = 'archive/<{0}:item_id>/unlock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'source': 'archive'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name


class ArchiveUnlockService(BaseService):

    def create(self, docs, **kwargs):
        user = get_user(required=True)
        c = get_component(ItemLock)
        item_id = request.view_args['item_id']
        c.unlock({'_id': item_id}, user['_id'], None)
        return [item_id]
