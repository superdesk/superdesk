import superdesk
from eve.io.base import DataLayer
from eve.io.mongo import Mongo
from eve.utils import config, ParsedRequest
from eve.defaults import resolve_default_values
from eve_elastic import Elastic
from .utils import import_by_path
from pyelasticsearch.client import JsonEncoder
from bson.objectid import ObjectId
from flask import current_app as app
from superdesk.datalayer_custom import CustomDataLayer


class SuperdeskJsonEncoder(JsonEncoder):
    '''Customize the JSON encoder used in Elastic'''
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        if isinstance(value, ObjectId):
            return str(value)
        return super(SuperdeskJsonEncoder, self).default(value)


class SuperdeskDataLayer(DataLayer):
    """Superdesk Data Layer"""

    serializers = Mongo.serializers
    serializers.update(Elastic.serializers)

    def init_app(self, app):
        self.mongo = Mongo(app)
        self.elastic = Elastic(app)
        self.custom = CustomDataLayer(app)
        self.elastic.es.json_encoder = SuperdeskJsonEncoder

        if 'DEFAULT_FILE_STORAGE' in app.config:
            self.storage = import_by_path(app.config['DEFAULT_FILE_STORAGE'])()
            self.storage.init_app(app)
        else:
            self.storage = self.driver

    def find(self, resource, req, lookup):
        return superdesk.get_resource_service(resource).get(req=req, lookup=lookup)

    def find_all(self, resource, max_results=1000):
        req = ParsedRequest()
        req.max_results = max_results
        return self._backend(resource).find(resource, req, None)

    def find_one(self, resource, req, **lookup):
        return superdesk.get_resource_service(resource).find_one(req=req, **lookup)

    def find_one_raw(self, resource, _id):
        return self._backend(resource).find_one_raw(resource, _id)

    def find_list_of_ids(self, resource, ids, client_projection=None):
        return self._backend(resource).find_list_of_ids(resource, ids, client_projection)

    def insert(self, resource, docs, **kwargs):
        for doc in docs:
            resolve_default_values(doc, app.config['DOMAIN'][resource]['defaults'])
        return superdesk.get_resource_service(resource).post(docs, **kwargs)

    def update(self, resource, id_, updates):
        return superdesk.get_resource_service(resource).patch(id=id_, updates=updates)

    def update_all(self, resource, query, updates):
        datasource = self._datasource(resource)
        driver = self._backend(resource).driver
        collection = driver.db[datasource[0]]
        return collection.update(query, {'$set': updates}, multi=True)

    def replace(self, resource, id_, document):
        resolve_default_values(document, app.config['DOMAIN'][resource]['defaults'])
        return superdesk.get_resource_service(resource).put(id=id_, document=document)

    def remove(self, resource, lookup=None):
        if lookup is None:
            lookup = {}
        return superdesk.get_resource_service(resource).delete_action(lookup=lookup)

    def is_empty(self, resource):
        return self._backend(resource).is_empty(resource)

    def _search_backend(self, resource):
        if resource.endswith(app.config['VERSIONS']):
            return
        datasource = self._datasource(resource)
        backend = config.SOURCES[datasource[0]].get('search_backend', None)
        return getattr(self, backend) if backend is not None else None

    def _backend(self, resource):
        datasource = self._datasource(resource)
        backend = config.SOURCES[datasource[0]].get('backend', 'mongo')
        return getattr(self, backend)
