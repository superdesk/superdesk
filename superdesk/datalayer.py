
from eve.io.mongo import Mongo
from eve.utils import config, ParsedRequest
from eve_elastic import Elastic
from pyelasticsearch.exceptions import IndexAlreadyExistsError
from .signals import send
from .utils import import_by_path


class SuperdeskDataLayer(Mongo):

    """Superdesk Data Layer"""

    serializers = Mongo.serializers
    serializers.update(Elastic.serializers)

    def init_app(self, app):
        Mongo.init_app(self, app)
        self.elastic = Elastic(app)

        if 'DEFAULT_FILE_STORAGE' in app.config:
            self.storage = import_by_path(app.config['DEFAULT_FILE_STORAGE'])()
            self.storage.init_app(app)
        else:
            self.storage = self.driver

        try:
            self.elastic.es.create_index(self.elastic.index)
        except IndexAlreadyExistsError:
            pass

        self.elastic.put_mapping(app)

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
        return self._backend(resource).find(resource, req, None)

    def find_one(self, resource, req=None, **lookup):
        return self._backend(resource).find_one(resource, req=req, **lookup)

    def find_list_of_ids(self, resource, ids, client_projection=None):
        return self._backend(resource).find_list_of_ids(resource, ids, client_projection)

    def insert(self, resource, docs, **kwargs):
        self._send('create', resource, docs=docs)
        return self._backend(resource).insert(resource, docs, **kwargs)

    def update(self, resource, id_, updates):
        self._send('update', resource, id=id_, updates=updates)
        return self._backend(resource).update(resource, id_, updates)

    def update_all(self, resource, query, updates):
        datasource = self._datasource(resource)
        driver = self._backend(resource).driver
        collection = driver.db[datasource[0]]
        return collection.update(query, {'$set': updates}, multi=True)

    def replace(self, resource, id_, document):
        self._send('update', resource, id=id_, updates=document)
        return self._backend(resource).replace(resource, id_, document)

    def remove(self, resource, lookup=None):
        if lookup is None:
            lookup = {}
        self._send('delete', resource, lookup=lookup)
        return self._backend(resource).remove(resource, lookup)

    def is_empty(self, resource):
        return self._backend(resource).is_empty(resource)

    def _backend(self, resource):
        datasource = self._datasource(resource)
        backend = config.SOURCES[datasource[0]].get('backend', 'mongo')
        if backend is 'mongo':
            return super(SuperdeskDataLayer, self)
        return getattr(self, backend)

    def _send(self, signal, resource, **kwargs):
        send(signal, self, resource=resource, **kwargs)
        send('%s:%s' % (signal, resource), self, **kwargs)
