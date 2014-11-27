
import logging
from flask import current_app as app
from eve.utils import document_etag
from superdesk.utc import utcnow
from .elastic_sync_backend import create


log = logging.getLogger(__name__)


class EveBackend():
    def find_one(self, endpoint_name, req, **lookup):
        backend = self._backend(endpoint_name)
        search_backend = self._lookup_backend(endpoint_name, fallback=True)
        if search_backend:
            item = search_backend.find_one(endpoint_name, req=req, **lookup)
        if search_backend and item is None:
            item = backend.find_one(endpoint_name, req=req, **lookup)
            if item:
                create(endpoint_name, [item])
        return item

    def find_one_in_base_backend(self, endpoint_name, req, **lookup):
        backend = self._backend(endpoint_name)
        return backend.find_one(endpoint_name, req=req, **lookup)

    def get(self, endpoint_name, req, lookup):
        backend = self._lookup_backend(endpoint_name, fallback=True)
        cursor = backend.find(endpoint_name, req, lookup)
        if not cursor.count():
            return cursor  # return 304 if not modified
        else:
            # but fetch without filter if there is a change
            req.if_modified_since = None
            return backend.find(endpoint_name, req, lookup)

    def create(self, endpoint_name, docs, **kwargs):
        """Insert documents into given collection.

        :param endpoint_name: api resource name
        :param docs: list of docs to be inserted
        """
        for doc in docs:
            doc.setdefault(app.config['ETAG'], document_etag(doc))
            self.set_default_dates(doc)

        backend = self._backend(endpoint_name)
        ids = backend.insert(endpoint_name, docs, **kwargs)
        search_backend = self._lookup_backend(endpoint_name)
        if search_backend:
            search_backend.insert(endpoint_name, docs, **kwargs)
        return ids

    def update(self, endpoint_name, id, updates):
        """Update document with given id.

        :param endpoint_name: api resource name
        :param id: document id
        :param updates: changes made to document
        """
        # change etag on update so following request will refetch it
        updates.setdefault(app.config['LAST_UPDATED'], utcnow())
        updates.setdefault(app.config['ETAG'], document_etag(updates))

        backend = self._backend(endpoint_name)
        res = backend.update(endpoint_name, id, updates)

        search_backend = self._lookup_backend(endpoint_name)
        if search_backend is not None:
            doc = backend.find_one(endpoint_name, req=None, _id=id)
            search_backend.update(endpoint_name, id, doc)

        return res if res is not None else updates

    def replace(self, endpoint_name, id, document):
        backend = self._backend(endpoint_name)
        res = backend.replace(endpoint_name, id, document)

        search_backend = self._lookup_backend(endpoint_name)
        if search_backend is not None:
            search_backend.replace(endpoint_name, id, document)
        return res

    def delete(self, endpoint_name, lookup):
        backend = self._backend(endpoint_name)
        res = backend.remove(endpoint_name, lookup)
        search_backend = self._lookup_backend(endpoint_name)
        if search_backend is not None:
            try:
                search_backend.remove(endpoint_name, lookup)
            except ValueError as ex:
                log.error(ex)
                pass
        return res

    def _datasource(self, endpoint_name):
        return app.data._datasource(endpoint_name)[0]

    def _backend(self, endpoint_name):
        return app.data._backend(endpoint_name)

    def _lookup_backend(self, endpoint_name, fallback=False):
        backend = app.data._search_backend(endpoint_name)
        if backend is None and fallback:
            backend = app.data._backend(endpoint_name)
        return backend

    def set_default_dates(self, doc):
        now = utcnow()
        doc.setdefault(app.config['DATE_CREATED'], now)
        doc.setdefault(app.config['LAST_UPDATED'], now)
