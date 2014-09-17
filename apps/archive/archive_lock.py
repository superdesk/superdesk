from flask import request, current_app as app
from superdesk.utc import utcnow
from superdesk.resource import Resource
from .common import get_user, item_url
from superdesk.services import BaseService
from superdesk.notification import push_notification


class ArchiveLockResource(Resource):
    endpoint_name = 'archive_lock'
    url = 'archive/<{0}:item_id>/lock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'source': 'archive'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name


class ArchiveLockService(BaseService):

    def post(self, docs, **kwargs):
        docs.clear()
        item_id = request.view_args['item_id']
        item = self.find_one(req=None, _id=item_id)
        if not item:
            print('item not found', item_id)
            return -1

        user = get_user(required=True)
        updates = {'lock_user': user.get('_id'), 'lock_time': utcnow()}
        ids = app.data.update('archive', item_id, updates)
        item['lock_user'] = user
        push_notification('item:lock', item=str(item.get('_id')), user=str(user))
        return ids


class ArchiveUnlockResource(Resource):
    endpoint_name = 'archive_unlock'
    url = 'archive/<{0}:item_id>/unlock'.format(item_url)
    schema = {'lock_user': {'type': 'string'}}
    datasource = {'source': 'archive'}
    resource_methods = ['GET', 'POST']
    resource_title = endpoint_name


class ArchiveUnlockService(BaseService):

    def post(self, docs, **kwargs):
        docs.clear()
        item_id = request.view_args['item_id']
        item = self.find_one(req=None, _id=item_id)
        updates = {'lock_user': None, 'lock_time': None, 'force_unlock': True}
        ids = app.data.update('archive', item_id, updates)
        push_notification('item:unlock', item=str(item.get('_id')))
        return ids
