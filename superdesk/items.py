
from datetime import datetime
from flask import request, url_for

import superdesk
import superdesk.tokens

from .utils import get_random_string
from . import signals 

class ItemConflictException(Exception):
    pass

def save_item(data, db=superdesk.db):
    now = datetime.utcnow()
    data.setdefault('guid', generate_guid())
    data.setdefault('firstCreated', now)
    data.setdefault('versionCreated', now)

    item = db.items.find_one({'guid': data.get('guid')})
    if item and item.get('versionCreated').time() >= data.get('versionCreated').time():
        raise ItemConflictException()
    elif item:
        data['_id'] = item.get('_id')

    db.items.save(data)
    data['_id'] = str(data['_id'])
    signals.send('item:save', data)
    return data

def update_item(data, guid, db=superdesk.db):
    data['versionCreated'] = datetime.utcnow()
    item = db.items.find_one({'guid': guid})
    item.update(data)
    db.items.save(item)
    return item

def generate_guid(db=superdesk.db):
    guid = get_random_string()
    while db.items.find_one({'guid': guid}):
        guid = get_random_string()
    return guid

def get_last_updated(db=superdesk.db):
    item = db.items.find_one(fields=['versionCreated'], sort=[('versionCreated', -1)])
    if item:
        return item.get('versionCreated')

def on_read_items(db, docs):
    for doc in docs:
        for content in doc.get('contents', []):
            if content.get('href'):
                content['href'] = '%s?auth_token=%s' % (content.get('href'), superdesk.tokens.get_token(db))

superdesk.connect('read:items', on_read_items)

schema = {
    'guid': {
        'type': 'string'
    },
    'version': {
        'type': 'string'
    },
    'headline': {
        'type': 'string'
    },
    'slugline': {
        'type': 'string'
    },
    'creditline': {
        'type': 'string'
    },
    'copyrightHolder': {
        'type': 'string'
    },
    'description': {
        'type': 'string'
    },
    'firstCreated': {
        'type': 'datetime'
    },
    'versionCreated': {
        'type': 'datetime'
    },
    'itemClass': {
        'type': 'string'
    },
    'provider': {
        'type': 'string'
    },
    'urgency': {
        'type': 'int'
    },
    'contents': {
        'type': 'list'
    },
    'groups': {
        'type': 'list'
    }
}

superdesk.DOMAIN.update({
    'items': {
        'item_title': 'newsItem',
        'additional_lookup': {
            'url': '[a-zA-Z0-9,.:-]+',
            'field': 'guid'
        },
        'schema': schema
    }
})
