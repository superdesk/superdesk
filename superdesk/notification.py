"""Superdesk change notifications"""

import superdesk
from superdesk.signals import connect
import logging
from superdesk.utc import utcnow
from threading import Timer
from eve.methods import post

log = logging.getLogger(__name__)

superdesk.domain('notification', {
    'schema': {
        'changes': {
            'type': 'dict',
#             'schema': {
#                 'type': 'dict',
#                 'schema': {
#                     'created': {
#                         'type': 'integer',
#                         'min': 0,
#                     },
#                     'updated': {
#                         'type': 'integer',
#                         'min': 0,
#                     },
#                     'deleted': {
#                         'type': 'integer',
#                         'min': 0,
#                     },
#                 },
#            },
            'allow_unknwon': True,
        },
        'created_on': {
            'type': 'datetime'
        }
    },
    'resource_methods': ['GET'],
    'item_methods': ['GET'],
})

PUSH_INTERVAL = 1

notifications = {}

def save_notification():
    # TODO: pymongo connect
    global notifications, timer
    old_notifications = notifications
    notifications = {}
    now, instances = utcnow(), []
    for name, changes in old_notifications.items():
        instances.append({'changes': {name:changes}, 'created_on': now})
    
    with superdesk.app.app_context():
#         with superdesk.app.request_context({'HTTP_HOST':'test', 'wsgi.url_scheme':'test',
#                                             'REQUEST_METHOD': 'test', }):
        superdesk.app.data.insert('notification', instances)
        
    Timer(PUSH_INTERVAL, save_notification).start()

# Timer(PUSH_INTERVAL, save_notification).start()

def push_notification(name, created=0, deleted=0, updated=0):
    log.info('Pushing for %s, created %s, deleted %s, updated %s', name, created, deleted, updated)
    if created == deleted == updated == 0: return
    
#     changes = notifications.get(name)
#     if changes == None:
#         changes = notifications[name] = {
#             'created': 0,
#             'updated': 0,
#             'deleted': 0
#         }
    
    changes = {
        'created': 0,
        'updated': 0,
        'deleted': 0
    }
    if created: changes['created'] += created
    if deleted: changes['deleted'] += deleted
    if updated: changes['updated'] += updated
    
    post('notification', payl={'changes': {name:changes}})
    # superdesk.app.data.insert('notification', [{'changes': {name:changes}, 'created_on': utcnow()}])

def on_create_media_archive(data, docs): push_notification('media_archive', created=1)

connect('notification', push_notification)
superdesk.connect('create:ingest', on_create_media_archive)
superdesk.connect('create:archive', on_create_media_archive)
superdesk.connect('create:archive_media', on_create_media_archive)
