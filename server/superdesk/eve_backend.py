# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from flask import current_app as app
from eve.utils import document_etag, config
from superdesk.utc import utcnow
from eve.methods.common import resolve_document_etag


class EveBackend():
    def find_one(self, endpoint_name, req, **lookup):
        backend = self._backend(endpoint_name)
        item = backend.find_one(endpoint_name, req=req, **lookup)
        search_backend = self._lookup_backend(endpoint_name, fallback=True)
        if search_backend:
            item_search = search_backend.find_one(endpoint_name, req=req, **lookup)
            if item is None:
                item = item_search
            elif item_search is None:
                search_backend.insert(endpoint_name, [item])
        return item

    def get(self, endpoint_name, req, lookup):
        backend = self._lookup_backend(endpoint_name, fallback=True)
        cursor = backend.find(endpoint_name, req, lookup)
        if not cursor.count():
            return cursor  # return 304 if not modified
        else:
            # but fetch without filter if there is a change
            req.if_modified_since = None
            return backend.find(endpoint_name, req, lookup)

    def get_from_mongo(self, endpoint_name, req, lookup):
        req.if_modified_since = None
        backend = self._backend(endpoint_name)
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
        ids = backend.insert(endpoint_name, docs)
        search_backend = self._lookup_backend(endpoint_name)
        if search_backend:
            search_backend.insert(endpoint_name, docs, **kwargs)
        return ids

    def update(self, endpoint_name, id, updates, original):
        """Update document with given id.

        :param endpoint_name: api resource name
        :param id: document id
        :param updates: changes made to document
        :param original: original document
        """
        # change etag on update so following request will refetch it
        updates.setdefault(app.config['LAST_UPDATED'], utcnow())
        if config.ETAG not in updates:
            updated = original.copy()
            updated.update(updates)
            resolve_document_etag(updated, endpoint_name)
            updates[config.ETAG] = updated[config.ETAG]
        return self.system_update(endpoint_name, id, updates, original)

    def system_update(self, endpoint_name, id, updates, original):
        """Only update what is provided, without affecting etag/last_updated.

        This is useful when you want to make some changes without affecting users.

        :param endpoint_name: api resource name
        :param id: document id
        :param updates: changes made to document
        :param original: original document
        """
        backend = self._backend(endpoint_name)
        res = backend.update(endpoint_name, id, updates, original)

        search_backend = self._lookup_backend(endpoint_name)
        if search_backend is not None:
            doc = backend.find_one(endpoint_name, req=None, _id=id)
            search_backend.update(endpoint_name, id, doc)

        return res if res is not None else updates

    def replace(self, endpoint_name, id, document, original):
        backend = self._backend(endpoint_name)
        res = backend.replace(endpoint_name, id, document, original)

        search_backend = self._lookup_backend(endpoint_name)
        if search_backend is not None:
            search_backend.replace(endpoint_name, id, document)
        return res

    def delete(self, endpoint_name, lookup):
        backend = self._backend(endpoint_name)
        res = backend.remove(endpoint_name, lookup)
        search_backend = self._lookup_backend(endpoint_name)
        if search_backend is not None:
            search_backend.remove(endpoint_name, lookup)
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
