
from datetime import datetime
from flask import request, url_for

from . import api, mongo
from . import rest
from .auth import auth_required
from .utils import get_random_string
from .io.reuters_token import ReutersTokenProvider
from . import signals 

tokenProvider = ReutersTokenProvider()

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

def save_item(data):
    now = datetime.utcnow()
    data.setdefault('guid', generate_guid())
    data.setdefault('firstCreated', now)
    data.setdefault('versionCreated', now)

    item = mongo.db.items.find_one({'guid': data.get('guid')})
    if item and item.get('versionCreated').time() >= data.get('versionCreated').time():
        raise ItemConflictException()
    elif item:
        data['_id'] = item.get('_id')

    mongo.db.items.save(data)
    data['_id'] = str(data['_id'])
    signals.send('item:save', data)
    return data

def update_item(data, guid):
    data['versionCreated'] = datetime.utcnow()
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

    def get_query(self):
        query = {}
        query.setdefault('itemClass', 'icls:composite')
        if request.args.get('q'):
            query['headline'] = {'$regex': request.args.get('q'), '$options': 'i'}
        if request.args.get('itemClass'):
            query['itemClass'] = {'$in': request.args.get('itemClass').split(",")}
        return query

    @auth_required
    def get(self):
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 25))
        query = self.get_query()
        raw_items = mongo.db.items.find(query).sort('firstCreated', -1).skip(skip).limit(limit + 1)
        items = [format_item(item) for item in raw_items]
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

api.add_resource(ItemResource, '/items/<string:guid>', endpoint='item')
#api.add_resource(items.ItemListResource, '/items')
