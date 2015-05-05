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

from eve.utils import ParsedRequest
from flask import current_app as app
from publicapi.errors import UnexpectedParameterError
from superdesk.services import BaseService
from urllib.parse import urljoin, quote


logger = logging.getLogger(__name__)


class ItemsService(BaseService):
    """
    A service that knows how to perform CRUD operations on the `item`
    content types.

    Serves mainly as a proxy to the data layer.
    """

    def find_one(self, req, **lookup):
        """Retrieve a specific item.

        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        :param dict lookup: requested item lookup, contains its ID

        :return: requested item (if found)
        :rtype: dict or None
        """
        request_params = req.args or {}
        params = list(request_params.keys())

        if len(params) > 0:
            if 'q' not in params:
                desc = "Unexpected parameter ({})".format(params[0])
            else:
                desc = (
                    "Filtering is not supported when retrieving a single "
                    "item (the \"q\" parameter)"
                )
            raise UnexpectedParameterError(desc=desc)

        return super().find_one(req, **lookup)

    def get(self, req, lookup):
        """Retrieve a list of items that match the filter criteria (if any)
        pssed along the HTTP request.

        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        :param dict lookup: sub-resource lookup from the endpoint URL

        :return: database results cursor object
        :rtype: `pymongo.cursor.Cursor`
        """
        if req is None:
            req = ParsedRequest()

        request_params = req.args or {}
        allowed_params = ('q',)

        for param in request_params.keys():
            if param not in allowed_params:
                raise UnexpectedParameterError(
                    desc="Unexpected parameter ({})".format(param)
                )

        if 'q' in request_params:
            req.where = request_params['q']

        return super().get(req, lookup)

    # TODO: add docstrings and tests for the methods below
    def _set_uri(self, doc):
        resource_url = app.config['PUBLICAPI_URL'] + '/' + app.config['URLS'][self.datasource] + '/'
        doc['uri'] = urljoin(resource_url, quote(doc['_id']))

    def on_fetched_item(self, doc):
        self._set_uri(doc)

    def on_fetched(self, res):
        for doc in res['_items']:
            self._set_uri(doc)
        return res
