from builtins import NotImplementedError


class DataLayer():
    def etag(self, doc):
        raise NotImplementedError()

    def find_one(self, resource, filter, projection, options):
        raise NotImplementedError()

    def find(self, resource, filter, projection, options):
        raise NotImplementedError()

    def create(self, resource, docs):
        raise NotImplementedError()

    def update(self, resource, filter, doc):
        raise NotImplementedError()

    def replace(self, resource, filter, doc):
        raise NotImplementedError()

    def delete(self, resource, filter):
        raise NotImplementedError()
