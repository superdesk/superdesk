import logging

from eve.methods.post import post_intern
import flask

from superdesk.notification import push_notification

from .base_model import BaseModel


log = logging.getLogger(__name__)


def init_app(app):
    auditModel = AuditModel(app=app)
    app.on_inserted += auditModel.on_generic_inserted
    app.on_updated += auditModel.on_generic_updated
    app.on_deleted_item += auditModel.on_generic_deleted

    ActivityModel(app=app)


class AuditModel(BaseModel):
    endpoint_name = 'audit'
    resource_methods = ['GET']
    item_methods = ['GET']
    schema = {
        'resource': {'type': 'string'},
        'action': {'type': 'string'},
        'extra': {'type': 'dict'},
        'user': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'users',
                'field': '_id',
                'embeddable': False
            }
        }
    }
    exclude = {endpoint_name, 'activity'}

    def on_generic_inserted(self, resource, docs):
        if resource in self.exclude:
            return

        user = getattr(flask.g, 'user', None)
        if not user:
            return

        audit = {
            'user': user.get('_id'),
            'resource': resource,
            'action': 'created',
            'extra': docs[0]
        }
        post_intern(self.endpoint_name, audit)

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
        post_intern(self.endpoint_name, audit)

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
        post_intern(self.endpoint_name, audit)


class ActivityModel(BaseModel):
    endpoint_name = 'activity'
    resource_methods = ['GET']
    item_methods = ['GET']
    schema = {
        'message': {'type': 'string'},
        'data': {'type': 'dict'},
        'user': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'users',
                'field': '_id',
                'embeddable': True
            }
        }
    }
    exclude = {endpoint_name, 'notification'}


def add_activity(msg, **data):
    user = getattr(flask.g, 'user', None)
    if not user:
        return

    post_intern(ActivityModel.endpoint_name, {
        'user': user.get('_id'),
        'message': msg,
        'data': data
    })
    push_notification(ActivityModel.endpoint_name, created=1, keys=(user.get('_id'),))
