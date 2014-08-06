"""Superdesk change notifications"""

import logging
from threading import Timer

from eve.methods.post import post_internal
from superdesk import app

from .base_model import BaseModel


log = logging.getLogger(__name__)


class NotificationModel(BaseModel):
    endpoint_name = 'notification'
    schema = {
        'changes': {
            'type': 'dict',
            'allow_unknwon': True,
        }

    }
    resource_methods = ['GET']
    item_methods = ['GET']


def init_app(flask_app):
    push_interval = flask_app.config.get('NOTIFICATION_PUSH_INTERVAL', 3)
    NotificationModel(flask_app)
    timer = Timer(push_interval, save_notification, args=(flask_app, push_interval))
    timer.daemon = True
    timer.start()


def save_notification(app, push_interval):
    notifications = app.extensions.pop('superdesk_notifications', None)
    if notifications:
        with app.test_request_context():
            log.info('Saving changes %s', notifications)
            post_internal('notification', {'changes': notifications})

    timer = Timer(push_interval, save_notification, args=(app, push_interval))
    timer.daemon = True
    timer.start()


def push_notification(name, created=0, deleted=0, updated=0, keys=()):
    log.info('Pushing for %s, created %s, deleted %s, updated %s', name, created, deleted, updated)
    if created == deleted == updated == 0:
        return

    notifications = app.extensions.setdefault('superdesk_notifications', {})

    changes = notifications.get(name)
    if changes is None:
        changes = notifications[name] = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'keys': [],
        }

    changes['created'] += created
    changes['deleted'] += deleted
    changes['updated'] += updated
    changes['keys'].extend(keys)
