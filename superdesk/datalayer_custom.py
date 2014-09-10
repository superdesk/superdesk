import superdesk
from eve.io.base import DataLayer
from eve.utils import config


class CustomDataLayer(DataLayer):
    def init_app(self, app):
        pass

    def find(self, resource, req, lookup):
        return superdesk.apps[resource].get(req=req, lookup=lookup)

    def find_one(self, resource, req, **lookup):
        return superdesk.apps[resource].find_one(req=req, **lookup)

    def insert(self, resource, docs, **kwargs):
        ids = [doc[config.ID_FIELD] for doc in docs]
        return ids

    def update(self, resource, id_, updates):
        return updates
