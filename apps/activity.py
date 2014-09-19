
import logging
import flask

from eve.methods.post import post_internal
from superdesk.notification import push_notification
from superdesk.resource import Resource
from superdesk.services import BaseService
import superdesk

log = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'audit'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    auditResource = AuditResource(endpoint_name, app=app, service=service)
    app.on_inserted += auditResource.on_generic_inserted
    app.on_updated += auditResource.on_generic_updated
    app.on_deleted_item += auditResource.on_generic_deleted

    endpoint_name = 'activity'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    ActivityResource(endpoint_name, app=app, service=service)


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

    def on_generic_inserted(self, resource, docs):
        if resource in self.exclude:
            return

        user = getattr(flask.g, 'user', None)
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

        post_internal(self.endpoint_name, audit)

    def on_generic_updated(self, resource, doc, original):
        if resource in self.exclude:
            return

        user = getattr(flask.g, 'user', None)
        if not user:
            return

        audit = {
            'user': user.get('_id'),
            'resource': resource,
            'action': 'updated',
            'extra': doc
        }
        post_internal(self.endpoint_name, audit)

    def on_generic_deleted(self, resource, doc):
        if resource in self.exclude:
            return

        user = getattr(flask.g, 'user', None)
        if not user:
            return

        audit = {
            'user': user.get('_id'),
            'resource': resource,
            'action': 'deleted',
            'extra': doc
        }
        post_internal(self.endpoint_name, audit)


class ActivityResource(Resource):
    endpoint_name = 'activity'
    resource_methods = ['GET']
    item_methods = ['GET', 'PATCH']
    schema = {
        'message': {'type': 'string'},
        'data': {'type': 'dict'},
        'read': {'type': 'dict'},
        'item': Resource.rel('archive', type='string'),
        'user': Resource.rel('users'),
    }
    exclude = {endpoint_name, 'notification'}
    datasource = {
        'default_sort': [('_created', -1)]
    }
    resource_preferences = {
        'email_notification': {
            'enabled': False,
            'options': {
                'type': 'bool',
                'default': False
            }
        }
    }


def add_activity(msg, item=None, notify=None, **data):
    """Add an activity into activity log.

    This will became part of current user activity log.

    If there is someone set to be notified it will make it into his notifications box.
    """
    activity = {
        'message': msg,
        'data': data,
    }

    user = getattr(flask.g, 'user', None)
    if user:
        activity['user'] = user.get('_id')

    if notify:
        activity['read'] = {str(_id): 0 for _id in notify}
    else:
        activity['read'] = {}

    if item:
        activity['item'] = str(item)

    post_internal(ActivityResource.endpoint_name, activity)
    push_notification(ActivityResource.endpoint_name, _dest=activity['read'])
