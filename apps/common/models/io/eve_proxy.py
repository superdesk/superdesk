from .data_layer import DataLayer
from eve.utils import ParsedRequest
from eve import ID_FIELD


class EveProxy(DataLayer):
    def __init__(self, eve_data_layer):
        self.eve_data_layer = eve_data_layer

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
        return self.eve_data_layer.insert(resource, docs, base_backend=True)

    def update(self, resource, filter, doc):
        return self.eve_data_layer.update(resource, filter[ID_FIELD], doc, base_backend=True)

    def replace(self, resource, filter, doc):
        return self.eve_data_layer.replace(resource, filter[ID_FIELD], doc, base_backend=True)

    def delete(self, resource, filter):
        return self.eve_data_layer.remove(resource, filter)
