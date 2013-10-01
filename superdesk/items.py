
from datetime import datetime
from flask import request, url_for

import superdesk
from .api import Resource
from .auth import auth_required
from .utils import get_random_string
from .io.reuters_token import tokenProvider
from . import signals 

class ItemConflictException(Exception):
    pass

def parse_date(date):
    if isinstance(date, datetime):
        return date
    else:
        return datetime.strptime(date + '+0000', '%Y-%m-%dT%H:%M:%S%z')

def format_item(item):
    item.pop('_id', None)
    item.setdefault('self_url', url_for('item', guid=item.get('guid')))
    item['versionCreated'] = parse_date(item['versionCreated'])
    item['firstCreated'] = parse_date(item['firstCreated'])
    for content in item.get('contents', []):
        if content.get('href'):
            content['href'] = '%s?auth_token=%s' % (content.get('href'), tokenProvider.get_token())
    return item

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

superdesk.DOMAIN.update({
    'items': {
        'item_title': 'newsItem',
        'resource_methods': ['GET', 'POST'],
        'additional_lookup': {
            'url': '[\w]+',
            'field': 'guid'
        },
        'schema': {
            'guid': {
                'type': 'string',
                'unique': True
            },
            'headline': {
                'type': 'string'
            },
            'slugline': {
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
        },
    }
})
