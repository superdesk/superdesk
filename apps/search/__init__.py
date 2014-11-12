
from flask import current_app as app, json
import superdesk


class SearchService(superdesk.Service):
    """Federated search service.

    It can search ingest/content/archive/spike at the same time.
    """

    def _get_query(self, req):
        args = getattr(req, 'args', {})
        return json.loads(args.get('source')) if args.get('source') else {}

    def get(self, req, lookup):
        """Run elastic search agains on multiple doc types."""
        elastic = app.data.elastic
        query = self._get_query(req)
        types = ['ingest', 'archive']
        hits = elastic.es.search(body=query, index=elastic.index, doc_type=types)
        docs = elastic._parse_hits(hits, 'ingest')  # any resource here will do
        for resource in types:
            response = {app.config['ITEMS']: [doc for doc in docs if doc['_type'] == resource]}
            getattr(app, 'on_fetched_resource')(resource, response)
            getattr(app, 'on_fetched_resource_%s' % resource)(response)
        return docs


class SearchResource(superdesk.Resource):
    resource_methods = ['GET']
    item_methods = []


def init_app(app):
    search_service = SearchService('archive', backend=superdesk.get_backend())
    SearchResource('search', app=app, service=search_service)
