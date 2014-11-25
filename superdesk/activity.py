
import logging
from flask import g

from superdesk.notification import push_notification
from superdesk.resource import Resource
from superdesk.services import BaseService
import superdesk
from bson.objectid import ObjectId

log = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'activity'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    ActivityResource(endpoint_name, app=app, service=service)

    endpoint_name = 'audit'
    service = AuditService(endpoint_name, backend=superdesk.get_backend())
    AuditResource(endpoint_name, app=app, service=service)
    app.on_inserted += service.on_generic_inserted
    app.on_updated += service.on_generic_updated
    app.on_deleted_item += service.on_generic_deleted


class AuditResource(Resource):
    endpoint_name = 'audit'
    resource_methods = ['GET']
    item_methods = ['GET']
    schema = {
        'resource': {'type': 'string'},
        'action': {'type': 'string'},
        'extra': {'type': 'dict'},
        'user': Resource.rel('users', False)
    }
    exclude = {endpoint_name, 'activity'}


class AuditService(BaseService):

    def on_generic_inserted(self, resource, docs):
        if resource in AuditResource.exclude:
            return

        user = getattr(g, 'user', None)
        if not user:
            return

        if not len(docs):
            return

        audit = {
            'user': user.get('_id'),
            'resource': resource,
            'action': 'created',
            'extra': docs[0]
        }

        self.post([audit])

    def on_generic_updated(self, resource, doc, original):
        if resource in AuditResource.exclude:
            return

        user = getattr(g, 'user', None)
        if not user:
            return

        audit = {
            'user': user.get('_id'),
            'resource': resource,
            'action': 'updated',
            'extra': doc
        }
        self.post([audit])

    def on_generic_deleted(self, resource, doc):
        if resource in AuditResource.exclude:
            return

        user = getattr(g, 'user', None)
        if not user:
            return

        audit = {
            'user': user.get('_id'),
            'resource': resource,
            'action': 'deleted',
            'extra': doc
        }
        self.post([audit])


class ActivityResource(Resource):
    endpoint_name = 'activity'
    resource_methods = ['GET']
    item_methods = ['GET', 'PATCH']
    schema = {
        'name': {'type': 'string'},
        'message': {'type': 'string'},
        'data': {'type': 'dict'},
        'read': {'type': 'dict'},
        'item': Resource.rel('archive', type='string'),
        'user': Resource.rel('users'),
        'desk': Resource.rel('desks')
    }
    exclude = {endpoint_name, 'notification'}
    datasource = {
        'default_sort': [('_created', -1)]
    }
    superdesk.register_default_user_preference('email:notification', {
        'type': 'bool',
        'enabled': True,
        'default': True,
        'label': 'Send notifications via email',
        'category': 'notifications'
    })


ACTIVITY_CREATE = 'create'
ACTIVITY_UPDATE = 'update'
ACTIVITY_DELETE = 'delete'


def add_activity(activity_name, msg, item=None, notify=None, **data):
    """Add an activity into activity log.

    This will became part of current user activity log.

    If there is someone set to be notified it will make it into his notifications box.
    """
    activity = {
        'name': activity_name,
        'message': msg,
        'data': data,
    }

    user = getattr(g, 'user', None)
    if user:
        activity['user'] = user.get('_id')

    if notify:
        activity['read'] = {str(_id): 0 for _id in notify}
    else:
        activity['read'] = {}

    if item:
        activity['item'] = str(item.get('guid'))
        if item.get('task') and item['task'].get('desk'):
            activity['desk'] = ObjectId(item['task']['desk'])

    superdesk.get_resource_service(ActivityResource.endpoint_name).post([activity])
    push_notification(ActivityResource.endpoint_name, _dest=activity['read'])
