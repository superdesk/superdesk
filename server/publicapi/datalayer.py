# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from superdesk.datalayer import SuperdeskDataLayer


class ApiDataLayer(SuperdeskDataLayer):
    """Custom data layer for the Public API.

    It delegates API requests to Superdesk's backend to retrieve data from it.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # here the backend represents the part of Superdesk that knows how
        # to communicate with the underlying storage (i.e. database)
        self.backend = superdesk.get_backend()

    def find(self, resource, req, sub_resource_lookup):
        """Retrieves a set of resource items from database.

        Invoked when a collection of resource items is requested (e.g.
        `/items/`).

        :param str resource: name of the resource to retrieve (e.g. 'packages')
        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        :param dict sub_resource_lookup: sub-resource lookup from the API
            endpoint URL

        :return: database cursor object
        """
        return self.backend.get(resource, req, sub_resource_lookup)

    def find_one(self, resource, req, **lookup):
        """Retrieve a single resource item from database.

        Invoked when a specific resource item is requested (e.g.
        `/items/<item_id>`).

        :param str resource: name of the requested resource (e.g. 'packages')
        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        :param dict lookup: the lookup fields, most likely an item ID

        :return: requested item (if found)
        :rtype: object or None
        """
        return self.backend.find_one(resource, req, **lookup)
