from eve.io.mongo import Mongo
from flask.ext.pymongo import PyMongo
from eve.io.base import ConnectionException


class LegalArchiveDataLayer(Mongo):
    """Superdesk Data Layer"""

    def init_app(self, app):
        try:
            self.driver = PyMongo(app, config_prefix='LEGAL_ARCHIVE')
        except Exception as e:
            raise ConnectionException(e)

    def delete(self, resource, lookup):
        self.remove(resource, lookup)

    def create(self, resource, docs, **kwargs):
        self.insert(resource, docs)
