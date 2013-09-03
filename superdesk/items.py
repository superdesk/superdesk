
from datetime import datetime
from flask import request

from . import mongo
from . import rest
from .auth import auth_required
from .io.reuters import get_token

def format_item(item):
    for content in item.get('contents', []):
        if content.get('href'):
            content['href'] = '%s?auth_token=%s' % (content.get('href'), get_token())
    return item

class ItemListResource(rest.Resource):

    @auth_required
    def get(self):
        query = {}
        query.setdefault('itemClass', 'icls:composite')

        if request.args.get('q'):
            query['headline'] = {'$regex': request.args.get('q'), '$options': 'i'}

        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 25))

        items = [format_item(item) for item in mongo.db.items.find(query).sort('firstCreated', -1).skip(skip).limit(limit + 1)]
        return {'items': items[:limit], 'has_next': len(items) > limit, 'has_prev': skip > 0}

    @auth_required
    def post(self):
        data = request.get_json()
        mongo.db.items.save(data)
        return data, 201

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
        data.pop('_id', None)
        data.pop('firstCreated', None)
        data['versionCreated'] = datetime.utcnow()
        mongo.db.items.update({'guid': guid}, {'$set': data})
        return self.get(guid)
