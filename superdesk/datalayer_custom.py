from eve.io.base import DataLayer

class CustomDataLayer(DataLayer):
    def init_app(self, app):
        pass

    def insert(self, resource, docs, **kwargs):
        return docs
