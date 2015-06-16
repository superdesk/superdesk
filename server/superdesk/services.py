# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from flask import current_app as app
from eve.defaults import resolve_default_values
from eve.utils import ParsedRequest, config
from eve.methods.common import resolve_document_etag


log = logging.getLogger(__name__)


class BaseService():
    """
    Base service for all endpoints, defines the basic implementation
    for CRUD datalayer functionality.
    """

    datasource = None

    def __init__(self, datasource=None, backend=None):
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

    def on_fetched(self, docs):
        pass

    def on_fetched_item(self, doc):
        pass

    def create(self, docs, **kwargs):
        ids = self.backend.create(self.datasource, docs, **kwargs)
        return ids

    def update(self, id, updates, original):
        return self.backend.update(self.datasource, id, updates, original)

    def system_update(self, id, updates, original):
        return self.backend.system_update(self.datasource, id, updates, original)

    def replace(self, id, document, original):
        res = self.backend.replace(self.datasource, id, document, original)
        return res

    def delete(self, lookup):
        res = self.backend.delete(self.datasource, lookup)
        return res

    def find_one(self, req, **lookup):
        res = self.backend.find_one(self.datasource, req=req, **lookup)
        return res

    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        return self.backend.get(self.datasource, req=req, lookup=lookup)

    def get_from_mongo(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        return self.backend.get_from_mongo(self.datasource, req=req, lookup=lookup)

    def post(self, docs, **kwargs):
        for doc in docs:
            resolve_default_values(doc, app.config['DOMAIN'][self.datasource]['defaults'])
        self.on_create(docs)
        resolve_document_etag(docs, self.datasource)
        ids = self.create(docs, **kwargs)
        self.on_created(docs)
        return ids

    def patch(self, id, updates):
        original = self.find_one(req=None, _id=id)
        updated = original.copy()
        self.on_update(updates, original)
        updated.update(updates)
        if config.IF_MATCH:
            resolve_document_etag(updated, self.datasource)
            updates[config.ETAG] = updated[config.ETAG]
        res = self.update(id, updates, original)
        self.on_updated(updates, original)
        return res

    def put(self, id, document):
        resolve_default_values(document, app.config['DOMAIN'][self.datasource]['defaults'])
        original = self.find_one(req=None, _id=id)
        self.on_replace(document, original)
        resolve_document_etag(document, self.datasource)
        res = self.replace(id, document, original)
        self.on_replaced(document, original)
        return res

    def delete_action(self, lookup=None):
        if lookup is None:
            lookup = {}

        if lookup:
            doc = self.find_one(req=None, **lookup)
            self.on_delete(doc)
        res = self.delete(lookup)

        if lookup and doc:
            self.on_deleted(doc)
        return res

    def is_authorized(self, **kwargs):
        """
        Subclass should override if the resource handled by the service has intrinsic privileges.
        :param kwargs: should have properties which help in authorizing the request
        :return: False if unauthorized and True if authorized
        """

        return True
