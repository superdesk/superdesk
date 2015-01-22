from superdesk import get_resource_service
from superdesk.services import BaseService
from eve.utils import ParsedRequest
import json


def init_parsed_request(elastic_query):
    parsed_request = ParsedRequest()
    parsed_request.args = {"source": json.dumps(elastic_query)}
    return parsed_request


class HighlightsService(BaseService):
    def on_delete(self, doc):
        service = get_resource_service('archive')
        highlights_id = str(doc['_id'])
        query = {'query': {'filtered': {'filter': {'term': {'highlights': highlights_id}}}}}
        req = init_parsed_request(query)
        proposedItems = service.get(req=req, lookup=None)
        for item in proposedItems:
            updates = item.get('highlights').remove(highlights_id)
            service.update(item['_id'], {'highlights': updates})


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
            if doc['highlights'] not in item.get('highlights', []):
                updates = item.get('highlights', [])
                updates.append(doc['highlights'])
                service.update(item['_id'], {'highlights': updates})
        return ids
