
import json
import apps.packages.package_service as package

from superdesk import get_resource_service
from superdesk.services import BaseService
from eve.utils import ParsedRequest
from superdesk.notification import push_notification


def init_parsed_request(elastic_query):
    parsed_request = ParsedRequest()
    parsed_request.args = {"source": json.dumps(elastic_query)}
    return parsed_request


def get_highlighted_items(highlights_id):
    """Get items marked for given highlight and passing date range query."""
    highlight = get_resource_service('highlights').find_one(req=None, _id=highlights_id)
    req = init_parsed_request({
        'query': {
            'filtered': {'filter': {'and': [
                {'range': {'versioncreated': {'gte': highlight.get('auto_insert', 'now/d')}}},
                {'term': {'highlights': str(highlights_id)}},
            ]}}
        },
        'sort': [
            {'versioncreated': 'desc'},
        ]
    })
    return get_resource_service('archive').get(req, lookup=None)


def init_highlight_package(doc):
    """Add to package items marked for doc highlight."""
    main_group = doc.get('groups')[1]
    items = get_highlighted_items(doc.get('highlight'))
    for item in items:
        main_group['refs'].append(package.get_item_ref(item))


def on_create_package(sender, docs):
    """Call init_highlight_package for each package with highlight reference."""
    for doc in docs:
        if doc.get('highlight'):
            init_highlight_package(doc)


class HighlightsService(BaseService):
    def on_delete(self, doc):
        service = get_resource_service('archive')
        highlights_id = str(doc['_id'])
        query = {'query': {'filtered': {'filter': {'term': {'highlights': highlights_id}}}}}
        req = init_parsed_request(query)
        proposedItems = service.get(req=req, lookup=None)
        for item in proposedItems:
            updates = item.get('highlights').remove(highlights_id)
            service.update(item['_id'], {'highlights': updates}, item)


class MarkedForHighlightsService(BaseService):
    def create(self, docs, **kwargs):
        """Toggle highlight status for given highlight and item."""
        service = get_resource_service('archive')
        ids = []
        for doc in docs:
            item = service.find_one(req=None, guid=doc['marked_item'])
            if not item:
                ids.append(None)
                continue
            ids.append(item['_id'])
            highlights = item.get('highlights', [])
            if not highlights:
                highlights = []
            if doc['highlights'] not in highlights:
                highlights.append(doc['highlights'])
            else:
                highlights = [h for h in highlights if h != doc['highlights']]
            updates = {
                'highlights': highlights,
                '_updated': item['_updated'],
                '_etag': item['_etag']
            }
            service.update(item['_id'], updates, item)
        push_notification('item:mark', marked=1)
        return ids

package.package_create_signal.connect(on_create_package)
