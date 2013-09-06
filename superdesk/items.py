
from datetime import datetime
from flask import request

from . import mongo
from . import rest
from .auth import auth_required
from .utils import get_random_string
from .io.reuters_token import ReutersTokenProvider

tokenProvider = ReutersTokenProvider()

def format_item(item):
    for content in item.get('contents', []):
        if content.get('href'):
            content['href'] = '%s?auth_token=%s' % (content.get('href'), tokenProvider.get_token())
    return item

def save_item(data):
    now = datetime.utcnow()
    data.setdefault('guid', generate_guid())
    data.setdefault('firstCreated', now)
    data.setdefault('versionCreated', now)
    mongo.db.items.save(data)
    return data

def update_item(data, guid):
    data.pop('_id', None)
    data.setdefault('versionCreated', datetime.utcnow())
    item = mongo.db.items.find_one({'guid': guid})
    item.update(data)
    mongo.db.items.save(item)
    return item

def generate_guid():
    guid = get_random_string()
    while mongo.db.items.find_one({'guid': guid}):
        guid = get_random_string()
    return guid

def get_last_updated():
    item = mongo.db.items.find_one(fields=['versionCreated'], sort=[('versionCreated', -1)])
    if item:
        return item.get('versionCreated')

class ItemListResource(rest.Resource):

    @auth_required
    def get(self):
        query = {}
        query.setdefault('itemClass', 'icls:picture')

        if request.args.get('q'):
            query['headline'] = {'$regex': request.args.get('q'), '$options': 'i'}

        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 25))

        items = [format_item(item) for item in mongo.db.items.find(query).sort('firstCreated', -1).skip(skip).limit(limit + 1)]
        return {'items': items[:limit], 'has_next': len(items) > limit, 'has_prev': skip > 0}

    @auth_required
    def post(self):
        item = save_item(request.get_json())
        return item, 201

class ItemResource(rest.Resource):

    def _get_item(self, guid):
        return mongo.db.items.find_one_or_404({'guid': guid})

    @auth_required
    def get(self, guid):
        item = self._get_item(guid)
        return format_item(item)

    @auth_required
    def put(self, guid):
        data = request.get_json()
        item = update_item(data, guid)
        return format_item(item)
