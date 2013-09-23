
from pyelasticsearch import ElasticHttpNotFoundError
from flask import request

from . import app
from . import api
from . import search
from . import items
from . import manager
from . import signals
from .auth import auth_required

def get_index():
    return app.config.get('ELASTICSEARCH_INDEX')

def save_item(data):
    id = data.pop('_id', None)
    search.index(get_index(), 'items', data, id=data.get('guid'))
    data.setdefault('_id', id)

class ItemListResource(items.ItemListResource):

    def get_query(self):
        sort = ['_score'] if request.args.get('q') else [{'firstCreated': 'desc'}]
        return {
            'query': {
                'filtered': {
                    'query': {
                        'query_string': {
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
            result = search.search(query, index=get_index())
            items_formated = [items.format_item(res['_source']) for res in result['hits']['hits']]
            return {
                'items': items_formated,
                'has_next': result['hits']['total'] > query['from'] + query['size'],
                'has_prev': query['from'] > 0,
                'total': result['hits']['total']
            }
        except ElasticHttpNotFoundError:
            return {'items': [], 'has_prev': False, 'has_next': False}

signals.connect('item:save', save_item)
api.add_resource(ItemListResource, '/items')

@manager.command
def delete_index():
    """Delete search index"""
    return search.delete_index(get_index())
