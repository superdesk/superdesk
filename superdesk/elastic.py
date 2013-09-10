
import blinker
from pyelasticsearch import ElasticHttpNotFoundError
from flask import request

from . import app
from . import search
from . import items
from . import rest
from .auth import auth_required

def save_item(data):
    search.index(app.config.get('ELASTIC_INDEX'), 'items', data, id=data.get('_id'))

blinker.signal('item:save').connect(save_item)

class ItemListResource(items.ItemListResource):

    def get_query(self):
        sort = ['_score'] if request.args.get('q') else [{'firstCreated': 'desc'}]
        return {
            'query': {
                'filtered': {
                    'query': {
                        'query_string': {
                            'default_field': 'headline',
                            'query': request.args.get('q', '*')
                        }
                    },
                    'filter': {
                        'terms': {'itemClass': request.args.get('itemClass', 'icls:composite').split(',')}
                    },
                },
            },
            'sort': sort,
            'from': int(request.args.get('skip', 0)),
            'size': int(request.args.get('total', 25)),
        }

    @auth_required
    def get(self):
        try:
            query = self.get_query()
            result = search.search(query, index=app.config.get('ELASTIC_INDEX'))
            items_formated = [items.format_item(res['_source']) for res in result['hits']['hits']]
            return {
                'items': items_formated,
                'has_next': result['hits']['total'] > query['from'] + query['size'],
                'has_prev': query['from'] > 0,
            }
        except ElasticHttpNotFoundError:
            return {'items': [], 'has_prev': False, 'has_next': False}
