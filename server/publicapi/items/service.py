# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import functools
import json
import logging

from datetime import datetime, timedelta
from eve.utils import ParsedRequest
from flask import current_app as app
from flask import request
from publicapi.errors import BadParameterValueError, UnexpectedParameterError
from publicapi.items import ItemsResource
from superdesk.services import BaseService
from superdesk.utc import utcnow
from urllib.parse import urljoin, urlparse, quote
from werkzeug.datastructures import MultiDict
from publicapi.assets import url_for_media
from publicapi.settings import DATE_FORMAT


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

        allowed_params = ('include_fields', 'exclude_fields')
        self._check_for_unknown_params(
            req, whitelist=allowed_params, allow_filtering=False)

        self._set_fields_filter(req)  # Eve's "projection"

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

        allowed_params = (
            'q', 'start_date', 'end_date',
            'include_fields', 'exclude_fields'
        )
        self._check_for_unknown_params(req, whitelist=allowed_params)

        # set the "q" filter
        request_params = req.args or {}
        query_filter = {}

        if 'q' in request_params:
            # TODO: add validation for the "q" parameter when we define its
            # format and implement the corresponding actions
            query_filter = json.loads(request_params['q'])

        # set the date range filter
        start_date, end_date = self._get_date_range(request_params)
        date_filter = self._create_date_range_filter(start_date, end_date)
        query_filter.update(date_filter)

        req.where = json.dumps(query_filter)

        self._set_fields_filter(req)  # Eve's "projection"

        return super().get(req, lookup)

    def on_fetched_item(self, document):
        """Event handler when a single item is retrieved from database.

        It triggers the post-processing of the fetched item.

        :param dict document: fetched MongoDB document representing the item
        """
        self._process_fetched_object(document)

    def on_fetched(self, result):
        """Event handler when a collection of items is retrieved from database.

        For each item in the fetched collection it triggers the post-processing
        of it.

        It also changes the default-generated HATEOAS "self" link so that it
        does not expose the internal DB query details, but instead reflects
        what the client has sent in request.

        :param dict result: dictionary contaning the list of MongoDB documents
            (the fetched items) and some metadata, e.g. pagination info
        """
        for document in result['_items']:
            self._process_fetched_object(document)

        if '_links' in result:  # might not be present if HATEOAS disabled
            url_parts = urlparse(request.url)
            result['_links']['self']['href'] = '{}?{}'.format(
                url_parts.path[1:],  # relative path, remove opening slash
                url_parts.query
            )

    def _process_fetched_object(self, document):
        """Does some processing on the raw document fetched from database.

        It sets the item's `uri` field and removes all the fields added by the
        `Eve` framework that are not part of the NINJS standard (except for
        the HATEOAS `_links` object).
        It also sets the URLs for all externally referenced media content.

        :param dict document: MongoDB document to process
        """
        document['uri'] = self._get_uri(document)

        for field_name in ('_id', '_etag', '_created', '_updated'):
            document.pop(field_name, None)

        if 'renditions' in document:
            for k, v in document['renditions'].items():
                if 'media' in v:
                    v['href'] = url_for_media(v['media'])

    def _get_uri(self, document):
        """Return the given document's `uri`.

        :param dict document: MongoDB document fetched from database
        """
        if document.get('type') == 'composite':
            endpoint_name = 'packages'
        else:
            endpoint_name = 'items'

        resource_url = '{api_url}/{endpoint}/'.format(
            api_url=app.config['PUBLICAPI_URL'],
            endpoint=app.config['URLS'][endpoint_name]
        )
        return urljoin(resource_url, quote(document['_id']))

    def _check_for_unknown_params(
        self, request, whitelist, allow_filtering=True
    ):
        """Check if the request contains only allowed parameters.

        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        :param whitelist: iterable containing the names of allowed parameters.
        :param bool allow_filtering: whether or not the filtering parameter is
            allowed (True by default). Used for disallowing it when retrieving
            a single object.

        :raises UnexpectedParameterError:
            * if the request contains a parameter that is not whitelisted
            * if the request contains more than one value for any of the
              parameters
        """
        request_params = (request.args or MultiDict())

        if not allow_filtering:
            err_msg = ("Filtering{} is not supported when retrieving a "
                       "single object (the \"{param}\" parameter)")

            if 'q' in request_params.keys():
                desc = err_msg.format('', param='q')
                raise UnexpectedParameterError(desc=desc)

            if 'start_date' in request_params.keys():
                desc = err_msg.format(' by date range', param='start_date')
                raise UnexpectedParameterError(desc=desc)

            if 'end_date' in request_params.keys():
                desc = err_msg.format(' by date range', param='end_date')
                raise UnexpectedParameterError(desc=desc)

        for param_name in request_params.keys():
            if param_name not in whitelist:
                raise UnexpectedParameterError(
                    desc="Unexpected parameter ({})".format(param_name)
                )

            if len(request_params.getlist(param_name)) > 1:
                desc = "Multiple values received for parameter ({})"
                raise UnexpectedParameterError(desc=desc.format(param_name))

    def _get_date_range(self, request_params):
        """Extract the start and end date limits from request parameters.

        If start and/or end date parameter is not present, a default value is
        returned for the missing parameter(s).

        :param dict request_params: request parameter names and their
            corresponding values

        :return: a (start_date, end_date) tuple with both values being
            instances of Python's datetime.date

        :raises BadParameterValueError:
            * if any of the dates is not in the ISO 8601 format
            * if any of the dates is set in the future
            * if the start date is bigger than the end date
        """
        # check date limits' format...
        err_msg = ("{} parameter must be a valid ISO 8601 date (YYYY-MM-DD) "
                   "without the time part")

        try:
            start_date = self._parse_iso_date(request_params.get('start_date'))
        except ValueError:
            raise BadParameterValueError(
                desc=err_msg.format('start_date')) from None

        try:
            end_date = self._parse_iso_date(request_params.get('end_date'))
        except ValueError:
            raise BadParameterValueError(
                desc=err_msg.format('end_date')) from None

        # disallow dates in the future...
        err_msg = (
            "{} date ({}) must not be set in the future "
            "(current server date (UTC): {})")
        today = utcnow().date()

        if (start_date is not None) and (start_date > today):
            raise BadParameterValueError(
                desc=err_msg.format(
                    'Start', start_date.isoformat(), today.isoformat()
                )
            )

        if (end_date is not None) and (end_date > today):
            raise BadParameterValueError(
                desc=err_msg.format(
                    'End', end_date.isoformat(), today.isoformat()
                )
            )

        # make sure that the date range limits make sense...
        if (
            (start_date is not None) and (end_date is not None) and
            (start_date > end_date)
        ):
            # NOTE: we allow start_date == end_date (for specific date queries)
            raise BadParameterValueError(
                desc="Start date must not be greater than end date")

        # set default date range values if missing...
        if end_date is None:
            end_date = today

        if start_date is None:
            start_date = end_date

        return start_date, end_date + timedelta(days=1)

    def _create_date_range_filter(self, start_date, end_date):
        """Create a MongoDB date range query filter from the given dates.

        If both the start date and the end date are None, an empty filter is
        returned. The filtering is performed on the `versioncreated` field in
        database.

        :param start_date: the minimum version creation date (inclusive)
        :type start_date: datetime.date or None
        :param end_date: the maximum version creation date (inclusive)
        :type end_date: datetime.date or None

        :return: MongoDB date range filter (as a dictionary)
        """
        if (start_date is None) and (end_date is None):
            return {}  # nothing to set for the date range filter

        date_filter = {'versioncreated': {}}

        if start_date is not None:
            date_filter['versioncreated']['$gte'] = self._format_date(start_date)

        if end_date is not None:
            # need to set it to strictly less than end_date + 1 day,
            # because internally dates are stored as datetimes
            date_filter['versioncreated']['$lt'] = self._format_date(end_date)

        return date_filter

    def _set_fields_filter(self, req):
        """Set content fields filter on the request object (the "projection")
        based on the request parameters.

        It causes some of the content fields to be excluded from the retrieved
        data.

        :param req: object representing the HTTP request
        :type req: `eve.utils.ParsedRequest`
        """
        request_params = req.args or {}

        include_fields, exclude_fields = \
            self._get_field_filter_params(request_params)
        projection = self._create_field_filter(include_fields, exclude_fields)

        req.projection = json.dumps(projection)

    def _get_field_filter_params(self, request_params):
        """Extract the list of content fields to keep in or remove from
        the response.

        The parameter names are `include_fields` and `exclude_fields`. Both are
        simple comma-separated lists, for example::

            exclude_fields=  field_1, field_2,field_3,, ,field_4,

        NOTE: any redundant spaces, empty field values and duplicate values are
        gracefully ignored and do not cause an error.

        :param dict request_params: request parameter names and their
            corresponding values

        :return: a (include_fields, exclude_fields) tuple with each item being
            either a `set` of field names (as strings) or None if the request
            does not contain the corresponding parameter

        :raises BadParameterValueError:
            * if the request contains both parameters at the same time
            * if any of the parameters contain an unknown field name (i.e. not
                defined in the resource schema)
            * if `exclude_params` parameter contains a field name that is
                required to be present in the response according to the NINJS
                standard
        """
        include_fields = request_params.get('include_fields')
        exclude_fields = request_params.get('exclude_fields')

        # parse field filter parameters...
        strip_items = functools.partial(map, lambda s: s.strip())
        remove_empty = functools.partial(filter, None)

        if include_fields is not None:
            include_fields = include_fields.split(',')
            include_fields = set(remove_empty(strip_items(include_fields)))

        if exclude_fields is not None:
            exclude_fields = exclude_fields.split(',')
            exclude_fields = set(remove_empty(strip_items(exclude_fields)))

        # check for semantically incorrect field filter values...
        if (include_fields is not None) and (exclude_fields is not None):
            err_msg = ('Cannot both include and exclude content fields '
                       'at the same time.')
            raise UnexpectedParameterError(desc=err_msg)

        if include_fields is not None:
            err_msg = 'Unknown content field to include ({}).'
            for field in include_fields:
                if field not in ItemsResource.schema:
                    raise BadParameterValueError(desc=err_msg.format(field))

        if exclude_fields is not None:
            if 'uri' in exclude_fields:
                err_msg = ('Cannot exclude a content field required by the '
                           'NINJS format (uri).')
                raise BadParameterValueError(desc=err_msg)

            err_msg = 'Unknown content field to exclude ({}).'
            for field in exclude_fields:
                if field not in ItemsResource.schema:
                    raise BadParameterValueError(desc=err_msg.format(field))

        return include_fields, exclude_fields

    def _create_field_filter(self, include_fields, exclude_fields):
        """Create an `Eve` projection object that explicitly includes/excludes
        particular content fields from results.

        At least one of the parameters *must* be None. The created projection
        uses either a whitlist or a blacklist approach (see below), it cannot
        use both at the same time.

        * If `include_fields` is not None, a blacklist approach is used. All
            fields are _omittted_ from the result, except for those listed in
            the `include_fields` set.
        * If `exclude_fields` is not None, a whitelist approach is used. All
            fields are _included_ in the result, except for those listed in the
            `exclude_fields` set.
        * If both parameters are None, no field filtering should be applied
        and an empty dictionary is returned.

        NOTE: fields required by the NINJS standard are _always_ included in
        the result, regardless of the field filtering parameters.

        :param include_fields: fields to explicitly include in result
        :type include_fields: set of strings or None
        :param exclude_fields: fields to explicitly exclude from result
        :type exclude_fields: set of strings or None

        :return: `Eve` projection filter (as a dictionary)
        """
        projection = {}

        if include_fields is not None:
            for field in include_fields:
                projection[field] = 1
        elif exclude_fields is not None:
            for field in exclude_fields:
                projection[field] = 0

        return projection

    @staticmethod
    def _parse_iso_date(date_str):
        """Create a date object from the given string in ISO 8601 format.

        :param date_str:
        :type date_str: str or None

        :return: resulting date object or None if None is given
        :rtype: datetime.date

        :raises ValueError: if `date_str` is not in the ISO 8601 date format
        """
        if date_str is None:
            return None
        else:
            return datetime.strptime(date_str, '%Y-%m-%d').date()

    @staticmethod
    def _format_date(date):
        return datetime.strftime(date, DATE_FORMAT)
