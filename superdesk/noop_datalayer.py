
from .signals import send
from eve.io.base import DataLayer


class NoopDataLayer(DataLayer):

    """
      Noop Data Layer is used in the case when it is needed to have custom CRUD implementation
      for resources
    """

    def init_app(self, app):
        pass

    def find(self, resource, req, lookup):
        return self._send('impl_find', resource, req=req, **lookup)

    def find_one(self, resource, req=None, **lookup):
        return self._send('impl_find_one', resource, req=req, **lookup)

    def insert(self, resource, docs, **kwargs):
        return self._send('impl_insert', resource, docs=docs, **kwargs)

    def update(self, resource, id_, updates):
        return self._send('impl_update', resource, id=id_, updates=updates)

    def remove(self, resource, lookup=None):
        return self._send('impl_delete', resource, lookup=lookup)

    def _send(self, signal, resource, **kwargs):
        result = send('%s:%s' % (signal, resource), self.app.data, **kwargs)
        if not result or len(result) == 0:
            raise NotImplementedError
        elif len(result) > 1:
            # TODO: define and raise TooManyImplementationsError
            raise NotImplementedError
        return result[0][1]
