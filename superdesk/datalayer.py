
from eve.io import DataLayer
from eve.io.mongo import Mongo
from eve.utils import config, ParsedRequest
from eve_elastic import Elastic
from .signals import send
from .utils import import_by_path


class SuperdeskDataLayer(DataLayer):
    """Superdesk Data Layer"""

    serializers = Mongo.serializers
    serializers.update(Elastic.serializers)

    def init_app(self, app):
        self.elastic = Elastic(app)
        self.mongo = Mongo(app)

        if 'DEFAULT_FILE_STORAGE' in app.config:
            self.storage = import_by_path(app.config['DEFAULT_FILE_STORAGE'])()
            self.storage.init_app(app)
        else:
            self.storage = self.mongo.driver

        self._init_elastic()

    def _init_elastic(self):
        """Put elasticsearch mapping."""
        # todo(petr): create a command to set mapping and use domain for mapping
        for typename in ('archive', 'ingest'):
            mapping = {}
            mapping[typename] = {'properties': {
                'uri': {'type': 'string', 'index': 'not_analyzed'},
                'guid': {'type': 'string', 'index': 'not_analyzed'},
                'firstcreated': {'type': 'date'},
                'versioncreated': {'type': 'date'},
                'version': {'type': 'string'},
                'subject': {
                    'properties': {
                        'name': {'type': 'string', 'index': 'not_analyzed'}
                    }
                }
            }}

            self.elastic.es.put_mapping(self.elastic.index, typename, mapping, ignore_conflicts=True)

    def find(self, resource, req, lookup):
        cursor = self._backend(resource).find(resource, req, lookup)
        if not cursor.count():
            return cursor  # return 304 if not modified
        else:
            # but fetch without filter if there is a change
            req.if_modified_since = None
            return self._backend(resource).find(resource, req, lookup)

    def find_all(self, resource, max_results=1000):
        req = ParsedRequest()
        req.max_results = max_results
        return self._backend(resource).find(resource, req)

    def find_one(self, resource, **lookup):
        return self._backend(resource).find_one(resource, **lookup)

    def find_list_of_ids(self, resource, ids, client_projection=None):
        return self._backend(resource).find_list_of_ids(resource, ids, client_projection)

    def insert(self, resource, docs, **kwargs):
        self._send('create', resource, docs=docs)
        return self._backend(resource).insert(resource, docs, **kwargs)

    def update(self, resource, id_, updates):
        self._send('update', resource, id=id_, updates=updates)
        return self._backend(resource).update(resource, id_, updates)

    def replace(self, resource, id_, document):
        self._send('update', resource, id=id_, updates=document)
        return self._backend(resource).replace(resource, id_, document)

    def remove(self, resource, id_=None):
        self._send('delete', resource, id_=id_)
        return self._backend(resource).remove(resource, id_)

    def _backend(self, resource):
        datasource, filter_, projection_, sort_ = self._datasource(resource)
        backend = config.SOURCES[datasource].get('backend', 'mongo')
        return getattr(self, backend)

    def _send(self, signal, resource, **kwargs):
        send(signal, self, resource=resource, **kwargs)
        send('%s:%s' % (signal, resource), self, **kwargs)
