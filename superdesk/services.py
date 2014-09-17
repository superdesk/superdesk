import logging


log = logging.getLogger(__name__)


class BaseService():
    '''
    Base service for all endpoints, defines the basic implementation
    for CRUD datalayer functionality.
    '''
    datasource = None

    def __init__(self, datasource, backend):
        self.backend = backend
        self.datasource = datasource

    def on_create(self, docs):
        pass

    def on_created(self, docs):
        pass

    def on_update(self, updates, original):
        pass

    def on_updated(self, updates, original):
        pass

    def on_replace(self, document, original):
        pass

    def on_replaced(self, document, original):
        pass

    def on_delete(self, doc):
        pass

    def on_deleted(self, doc):
        pass

    def create(self, docs, **kwargs):
        ids = self.backend.create(self.datasource, docs, **kwargs)
        return ids

    def update(self, id, updates):
        res = self.backend.update(self.datasource, id, updates)
        return res

    def replace(self, id, document):
        res = self.backend.replace(self.datasource, id, document)
        return res

    def delete(self, lookup):
        res = self.backend.delete(self.datasource, lookup)
        return res

    def find_one(self, req, **lookup):
        res = self.backend.find_one(self.datasource, req=req, **lookup)
        return res

    def get(self, req, lookup):
        return self.backend.get(self.datasource, req=req, lookup=lookup)

    def post(self, docs, **kwargs):
        self.on_create(docs)
        ids = self.create(docs, **kwargs)
        self.on_created(docs)
        return ids

    def patch(self, id, updates):
        original = self.find_one(req=None, _id=id)
        self.on_update(updates, original)
        res = self.update(id, updates)
        self.on_updated(updates, original)
        return res

    def put(self, id, document):
        original = self.find_one(req=None, _id=id)
        self.on_replace(document, original)
        res = self.replace(id, document)
        self.on_replaced(document, original)
        return res

    def delete_action(self, lookup):
        if lookup:
            doc = self.find_one(req=None, **lookup)
            self.on_delete(doc)
        res = self.delete(lookup)
        if lookup and doc:
            self.on_deleted(doc)
        return res
