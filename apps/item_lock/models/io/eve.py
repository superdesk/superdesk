from .data_layer import DataLayer
from flask import current_app as app
from eve.utils import ParsedRequest
from eve import ID_FIELD


class Eve(DataLayer):
    def find_one(self, resource, filter, projection):
        req = ParsedRequest()
        req.args = {}
        req.projection = projection
        return app.data.find_one(resource, req, **filter)

    def find(self, resource, filter, projection, **options):
        req = ParsedRequest()
        req.args = {}
        req.projection = projection
        return app.data.find(resource, req, filter)

    def create(self, resource, docs):
        return app.data.insert(resource, docs)

    def update(self, resource, filter, doc):
        return app.data.update(resource, filter[ID_FIELD], doc)

    def replace(self, resource, filter, doc):
        return app.data.replace(resource, filter[ID_FIELD], doc)

    def delete(self, resource, filter):
        return app.data.replace(resource, filter)
