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
from publicapi.errors import BadParameterValueError, UnexpectedParameterError
from superdesk.services import BaseService
from urllib.parse import urljoin, quote
from werkzeug.datastructures import MultiDict


logger = logging.getLogger(__name__)


class ItemsService(BaseService):
    """
    A service that knows how to perform CRUD operations on the `item`
    content types.

    Serves mainly as a proxy to the data layer.
    """

    def _check_request_params(self, request, whitelist, allow_filtering=True):
        """Check if the request contains only valid parameters.

        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        :param whitelist: iterable containing the names of allowed parameters.
        :param bool allow_filtering: whether or not the filtering parameter is
            allowed (True by default). Used for disallowing it when retrieving
            a single object.

        :raises BadParameterValueError: if the request contains more than one
            value for any of the parameters
        :raises UnexpectedParameterError: if the request contains a parameter
            that is not whitelisted
        """
        request_params = (request.args or MultiDict())

        if not allow_filtering and 'q' in request_params.keys():
            desc = (
                "Filtering is not supported when retrieving a single "
                "object (the \"q\" parameter)"
            )
            raise UnexpectedParameterError(desc=desc)

        for param_name in request_params.keys():
            if param_name not in whitelist:
                raise UnexpectedParameterError(
                    desc="Unexpected parameter ({})".format(param_name)
                )

            if len(request_params.getlist(param_name)) > 1:
                desc = "Multiple values received for parameter ({})"
                raise BadParameterValueError(desc=desc.format(param_name))

    def find_one(self, req, **lookup):
        """Retrieve a specific item.

        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        :param dict lookup: requested item lookup, contains its ID

        :return: requested item (if found)
        :rtype: dict or None
        """
        self._check_request_params(req, whitelist=(), allow_filtering=False)

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

        self._check_request_params(req, whitelist=('q',))

        request_params = req.args or {}
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
