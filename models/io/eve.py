from models.io.data_layer import DataLayer
from eve.utils import ParsedRequest
from flask import current_app as app
from eve import ID_FIELD


class Eve(DataLayer):
    def find_one(self, resource, filter, projection):
        return app.data.find_one(resource, ParsedRequest(), **filter)

    def find(self, resource, filter, projection, **options):
        return app.data.find(resource, ParsedRequest(), filter, **options)

    def create(self, resource, docs):
        return app.data.insert(resource, docs)

    def update(self, resource, filter, doc):
        return app.data.update(resource, filter[ID_FIELD], doc)

    def replace(self, resource, filter, doc):
        return app.data.replace(resource, filter[ID_FIELD], doc)

    def delete(self, resource, filter):
        return app.data.replace(resource, filter)
