# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json
import logging

from datetime import datetime
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

    def find_one(self, req, **lookup):
        """Retrieve a specific item.

        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        :param dict lookup: requested item lookup, contains its ID

        :return: requested item (if found)
        :rtype: dict or None
        """
        if req is None:
            req = ParsedRequest()

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

        allowed_params = ('q', 'start_date', 'end_date')
        self._check_request_params(req, whitelist=allowed_params)

        request_params = req.args or {}
        query_filter = {}

        # set the "q" filter
        if 'q' in request_params:
            # TODO: add validation for the "q" parameter when we define its
            # format and implement the corresponding actions
            query_filter = json.loads(request_params['q'])

        # set the date range filter
        start_date, end_date = self._get_date_range(request_params)
        date_filter = self._create_date_range_filter(start_date, end_date)
        query_filter.update(date_filter)

        req.where = json.dumps(query_filter)

        return super().get(req, lookup)

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

    def _get_date_range(self, request_params):
        """TODO: helper method  to extract day, srt default values etc."""
        # TODO: add tests, comments, format checking, implement...

        # TODO: validate date format! helper function..
        # check for no ValueError: datetime.strptime(date_text, '%Y-%m-%d')
        # if yes, raise BadParameterValueError (from None, of course)

        start_date = request_params.get('start_date')
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        end_date = request_params.get('end_date')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        return start_date, end_date

    def _create_date_range_filter(self, start_date, end_date):
        """TODO: docstrings, perhaps tests etc."""
        if (start_date is None) and (end_date is None):
            return {}  # nothing to set for the date range filter

        date_filter = {'versioncreated': {}}

        if start_date is not None:
            date_filter['versioncreated']['$gte'] = start_date.isoformat()

        if end_date is not None:
            date_filter['versioncreated']['$lte'] = end_date.isoformat()

        return date_filter

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
