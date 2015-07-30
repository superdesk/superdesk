# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from eve.io.base import DataLayer
from eve.io.mongo import Mongo
from eve.utils import config, ParsedRequest
from eve_elastic import Elastic
from flask import current_app as app
from superdesk.aap_mm_datalayer import AAPMMDatalayer


class SuperdeskDataLayer(DataLayer):
    """Superdesk Data Layer"""

    serializers = Mongo.serializers
    serializers.update(Elastic.serializers)

    def init_app(self, app):
        self.mongo = Mongo(app)
        self.elastic = Elastic(app)
        self.aapmm = AAPMMDatalayer(app)
        self.driver = self.mongo.driver
        self.storage = self.driver

    def find(self, resource, req, lookup):
        return superdesk.get_resource_service(resource).get(req=req, lookup=lookup)

    def find_all(self, resource, max_results=1000):
        req = ParsedRequest()
        req.max_results = max_results
        return self._backend(resource).find(resource, req, None)

    def find_one(self, resource, req, **lookup):
        return superdesk.get_resource_service(resource).find_one(req=req, **lookup)

    def find_one_raw(self, resource, _id):
        return self._backend(resource).find_one_raw(resource, _id)

    def find_list_of_ids(self, resource, ids, client_projection=None):
        return self._backend(resource).find_list_of_ids(resource, ids, client_projection)

    def insert(self, resource, docs, **kwargs):
        return superdesk.get_resource_service(resource).create(docs, **kwargs)

    def update(self, resource, id_, updates, original):
        return superdesk.get_resource_service(resource).update(id=id_, updates=updates, original=original)

    def update_all(self, resource, query, updates):
        datasource = self.datasource(resource)
        driver = self._backend(resource).driver
        collection = driver.db[datasource[0]]
        return collection.update(query, {'$set': updates}, multi=True)

    def replace(self, resource, id_, document, original):
        return superdesk.get_resource_service(resource).replace(id=id_, document=document, original=original)

    def remove(self, resource, lookup=None):
        if lookup is None:
            lookup = {}
        return superdesk.get_resource_service(resource).delete(lookup=lookup)

    def is_empty(self, resource):
        return self._backend(resource).is_empty(resource)

    def _search_backend(self, resource):
        if resource.endswith(app.config['VERSIONS']):
            return
        datasource = self.datasource(resource)
        backend = config.SOURCES.get(datasource[0], {}).get('search_backend', None)
        return getattr(self, backend) if backend is not None else None

    def _backend(self, resource):
        datasource = self.datasource(resource)
        backend = config.SOURCES.get(datasource[0], {'backend': 'mongo'}).get('backend', 'mongo')
        return getattr(self, backend)
