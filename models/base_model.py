class InvalidFilter(Exception):
    def __init__(self, filter, operation):
        self.filter = filter
        self.operation = operation

    def __src__(self):
        return 'Invalid filter on %s: %s' % (self.operation, filter)

class BaseModel():
    def __init__(self, resource, data_layer, schema, validator):
        self.resource = resource
        self.data_layer = data_layer
        self.schema = schema

    def on_create(self, docs):
        '''
        Method called before the create operation.
        @param docs: list of docs to be inserted
        '''

    def on_created(self, docs):
        '''
        Method called after the create operation.
        @param docs: list of inserted docs
        '''

    def on_update(self, doc, orig):
        '''
        Method called before the update/replace operations.
        @param doc: the document updates
        @param orig: the original document before the update
        '''

    def on_updated(self, doc, orig):
        '''
        Method called after the update/replace operations.
        @param doc: the document updates
        @param orig: the original document before the update
        '''

    def on_delete(self, docs):
        '''
        Method called before the delete operation.
        @param docs: list of docs to be deleted
        '''

    def on_deleted(self, docs):
        '''
        Method called after the delete operation.
        @param docs: list of deleted docs
        '''

    def find_one(self, filter, projection):
        '''
        Return one document selected based on the given filter.
        @param filter: dict
        @param projection: dict
        '''
        return self.data_layer.find_one(filter, projection)

    def find(self, filter, projection, options):
        '''
        Return a list of documents selected based on the given filter.
        @param filter: dict
        @param projection: dict
        @param options: dict
        '''
        return self.data_layer.find(filter, projection, options)

    def create(self, docs):
        '''
        Insert a list of documents
        @param docs: list
        '''
        errors = self.validate(docs)
        self.on_create(docs)
        res = self.data_layer.create(docs)
        self.on_created(docs)
        self.add_errors(res, errors)
        return res

    def update(self, filter, doc):
        '''
        Update one document selected based on the given filter.
        @param filter: dict
        @param doc: dict
        '''
        self.validate(doc)
        orig = self.find(filter)
        if len(orig) > 1:
            raise InvalidFilter(filter, 'update')
        if len(orig) == 0:
            return
        self.on_update(doc, orig[0])
        res = self.data_layer.replace(filter, doc)
        self.on_updated(doc, orig[0])
        return res

    def replace(self, filter, doc):
        '''
        Replace the content of one document selected based on the given filter.
        @param filter: dict
        @param doc: dict
        '''
        self.validate(doc)
        orig = self.find(filter)
        if len(orig) != 1:
            raise InvalidFilter(filter, 'replace')
        self.on_update(doc, orig[0])
        res = self.data_layer.update(filter, doc)
        self.on_updated(doc, orig[0])
        return res

    def delete(self, filter):
        '''
        Delete one document selected based on the given filter.
        @param filter: dict
        '''
        orig = self.find(filter)
        if not orig:
            return
        self.on_delete(orig)
        res = self.data_layer.delete(filter)
        self.on_deleted(orig)
        return res

    def validate(self, docs):
        '''
        Validate a document or a list of documents.
        @param docs: list of documents
        '''
        errs = []
        if not isinstance(docs, list):
            docs = [docs]
        for doc in docs:
            err = self.validator.validate(doc)
            if errs:
                errs.append(err)
        return errs

    def add_errors(self, res, errors):
        # TODO: implement
        pass
