# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


# TODO: implement a custom data layer that knows how to fetch data
# from Superdesk (i.e. byusing Superdesk's existing data layer)
# basically we need to subclass eve.io.base. DataLayer class
# (only themethods for reading data, writing not needed for now)

# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.io.base import DataLayer
from eve.utils import config
from flask import current_app as app

from eve.io.mongo import Mongo
from eve_elastic import Elastic
from superdesk.utils import import_by_path

import superdesk
from superdesk.datalayer import SuperdeskDataLayer


class ApiDataLayer(DataLayer):
    """Public API Data Layer"""

    # TODO: directly subclass superdesk.datalayer? perhaps
    # get rid of the stuff in init_app?

    def init_app(self, app):
        print('ApiDataLayer.init_app called')

        # XXX: how to get rid of this Mongo initialization? call superdesk's
        # DataLayer.init_app()?
        self.mongo = Mongo(app)
        self.elastic = Elastic(app)

        if 'DEFAULT_FILE_STORAGE' in app.config:
            self.storage = import_by_path(app.config['DEFAULT_FILE_STORAGE'])()
            self.storage.init_app(app)
        else:
            self.storage = self.driver

    def find(self, resource, req, sub_resource_lookup):
        """
        resource: endpoint name (e.g. 'packages') - samo v tem kontekstu,
            sicer je to (datasource) ime dokumenta / collectiona v Elasticu
            oz. MongoDB
        req: eve.utils.ParsedRequest - parsed request object
          req.args - parsed querystring params
        sub_resource_lookup: sub-resource lookup from the endpoint url
        """
        backend = superdesk.get_backend()
        return backend.get(resource, req, sub_resource_lookup)

    def find_all(self, resource, max_results=1000):
        import pdb; pdb.set_trace()
        req = ParsedRequest()
        req.max_results = max_results
        return self._backend(resource).find(resource, req, None)

    def find_one(self, resource, req, **sub_resource_lookup):
        #
        # example item IDs (the value of sub_resource_lookup parameter)
        # { "_id" : "tag:localhost:2015:f4b35e12-559b-4a2b-b1f2-d5e64048bde8" }
        # { "_id" : "urn:newsml:localhost:2015-04-08T15:13:09.815503:8a907111-4310-43cc-8acd-957c5b135a5e" }

        backend = superdesk.get_backend()  # XXX: have this in __init__?
        return backend.find_one(resource, req, **sub_resource_lookup)

    def find_one_raw(self, resource, _id):
        import pdb; pdb.set_trace()
        return self._backend(resource).find_one_raw(resource, _id)

    def find_list_of_ids(self, resource, ids, client_projection=None):
        import pdb; pdb.set_trace()
        return self._backend(resource).find_list_of_ids(resource, ids, client_projection)

    def is_empty(self, resource):
        import pdb; pdb.set_trace()
        return self._backend(resource).is_empty(resource)

    def _search_backend(self, resource):
        if resource.endswith(app.config['VERSIONS']):
            return
        datasource = self._datasource(resource)
        backend = config.SOURCES[datasource[0]].get('search_backend', None)
        # XXX: backend is always None for now, thus a fallback is used
        return getattr(self, backend) if backend is not None else None

    def _backend(self, resource):
        datasource = self._datasource(resource)
        backend = config.SOURCES[datasource[0]].get('backend', 'mongo')
        # this becomes 'mongo', but self.mongo does not exist
        return getattr(self, backend)
