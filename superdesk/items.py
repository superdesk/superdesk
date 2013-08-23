
from flask import request
import api
from auth.decorators import auth_required
from superdesk import mongo

def format_item(item):
    return item

class ItemListResource(api.Resource):

    @auth_required
    def get(self):
        query = {}
        query.setdefault('itemClass', 'icls:text')

        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 25))

        items = [format_item(item) for item in mongo.db.items.find(query).sort('firstCreated', -1).skip(skip).limit(limit + 1)]
        return {'items': items[:limit], 'has_next': len(items) > limit, 'has_prev': skip > 0}

    @auth_required
    def post(self):
        pass

class ItemResource(api.Resource):

    @auth_required
    def get(self, guid):
        item = mongo.db.items.find_one({'guid': guid})
        if item:
            return format_item(item)
        else:
            return {'message': "item not found", 'code': 404}, 404
