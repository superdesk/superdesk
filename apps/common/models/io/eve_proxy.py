from .data_layer import DataLayer
from eve.utils import ParsedRequest, config, document_etag
from eve import ID_FIELD


class EveProxy(DataLayer):
    '''
    Data layer implementation used to connect the models to the Eve data layer.
    Transforms the model data layer API into Eve data layer calls.
    '''
    def __init__(self, eve_data_layer):
        self.eve_data_layer = eve_data_layer

    def etag(self, doc):
        return doc.get(config.ETAG, document_etag(doc))

    def find_one(self, resource, filter, projection):
        req = ParsedRequest()
        req.args = {}
        req.projection = projection
        return self.eve_data_layer.find_one(resource, req, **filter)

    def find(self, resource, filter, projection, **options):
        req = ParsedRequest()
        req.args = {}
        req.projection = projection
        return self.eve_data_layer.find(resource, req, filter)

    def create(self, resource, docs):
        return self.eve_data_layer.insert(resource, docs)

    def update(self, resource, filter, doc):
        return self.eve_data_layer.update(resource, filter[ID_FIELD], doc)

    def replace(self, resource, filter, doc):
        return self.eve_data_layer.replace(resource, filter[ID_FIELD], doc)

    def delete(self, resource, filter):
        return self.eve_data_layer.remove(resource, filter)
