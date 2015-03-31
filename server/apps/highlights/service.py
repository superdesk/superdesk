
import json
import apps.archive.archive_composite as package

from superdesk import get_resource_service
from superdesk.services import BaseService
from eve.utils import ParsedRequest
from superdesk.notification import push_notification


def init_parsed_request(elastic_query):
    parsed_request = ParsedRequest()
    parsed_request.args = {"source": json.dumps(elastic_query)}
    return parsed_request


def init_highlight_package(doc):
    """Add to package items marked for doc highlight."""
    main_group = doc.get('groups')[1]
    items = get_resource_service('archive').get(None, {'highlights': str(doc.get('highlight'))})
    assert items.count() == 2, items.count()
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
                service.update(item['_id'], {'highlights': highlights}, item)
            push_notification('item:mark', marked=1)
        return ids

package.package_create_signal.connect(on_create_package)
