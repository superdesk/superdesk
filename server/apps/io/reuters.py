# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Reuters io service."""

import traceback
import datetime
from urllib.parse import urlparse, urlunparse

import requests

from superdesk.io.ingest_service import IngestService

from superdesk.utc import utcnow
from superdesk.etree import etree, ParseError
from superdesk.io.newsml_2_0 import NewsMLTwoParser
from .reuters_token import get_token
from superdesk.errors import IngestApiError
from flask import current_app as app


class ReutersIngestService(IngestService):
    """Reuters ingest service."""

    PROVIDER = 'reuters'

    ERRORS = [IngestApiError.apiTimeoutError().get_error_description(),
              IngestApiError.apiRedirectError().get_error_description(),
              IngestApiError.apiRequestError().get_error_description(),
              IngestApiError.apiUnicodeError().get_error_description(),
              IngestApiError.apiParseError().get_error_description(),
              IngestApiError.apiGeneralError().get_error_description()]

    DATE_FORMAT = '%Y.%m.%d.%H.%M'
    URL = 'http://rmb.reuters.com/rmd/rest/xml'
    token = None

    def __init__(self):
        self.parser = NewsMLTwoParser()

    def get_token(self):
        """Get reuters token once for an update run."""
        if not self.token:
            self.token = get_token(self.provider, update=True)
        return self.token

    def _update(self, provider):
        """Service update call."""
        self.provider = provider
        updated = utcnow()

        last_updated = provider.get('last_updated')
        ttl_minutes = app.config['INGEST_EXPIRY_MINUTES']
        if not last_updated or last_updated < updated - datetime.timedelta(minutes=ttl_minutes):
            last_updated = updated - datetime.timedelta(minutes=ttl_minutes)

        for channel in self.get_channels():
            for guid in self.get_ids(channel, last_updated, updated):
                items = self.fetch_ingest(guid)
                if items:
                    yield items

    def fetch_ingest(self, guid):
        items = self.get_items(guid)
        result_items = []
        while items:
            item = items.pop()
            self.add_timestamps(item)
            try:
                items.extend(self.fetch_assets(item))
                result_items.append(item)
            except LookupError as err:
                self.log_item_error(err, item, self.provider)
                return []
        return result_items

    def fetch_assets(self, item):
        """Fetch remote assets for given item."""
        items = []
        for group in item.get('groups', []):
            for ref in group.get('refs', []):
                if 'residRef' in ref:
                    items.extend(self.get_items(ref.get('residRef')))
        return items

    def get_items(self, guid):
        """Parse item message and return given items."""
        payload = {'id': guid}
        tree = self.get_tree('item', payload)
        items = self.parser.parse_message(tree, self.provider)
        return items

    def get_ids(self, channel, last_updated, updated):
        """Get ids of documents which should be updated."""
        ids = []
        payload = {'channel': channel, 'fieldsRef': 'id'}
        payload['dateRange'] = "%s-%s" % (self.format_date(last_updated), self.format_date(updated))
        tree = self.get_tree('items', payload)
        for result in tree.findall('result'):
            ids.append(result.find('guid').text)
        return ids

    def get_channels(self):
        """Get subscribed channels."""
        channels = []
        tree = self.get_tree('channels')
        for channel in tree.findall('channelInformation'):
            channels.append(channel.find('alias').text)
        return channels

    def get_tree(self, endpoint, payload=None):
        """Get xml response for given API endpoint and payload."""
        if payload is None:
            payload = {}
        payload['token'] = self.get_token()
        url = self.get_url(endpoint)

        try:
            response = requests.get(url, params=payload, timeout=15)
        except requests.exceptions.Timeout as ex:
            # Maybe set up for a retry, or continue in a retry loop
            raise IngestApiError.apiTimeoutError(ex, self.provider)
        except requests.exceptions.TooManyRedirects as ex:
            # Tell the user their URL was bad and try a different one
            raise IngestApiError.apiRedirectError(ex, self.provider)
        except requests.exceptions.RequestException as ex:
            # catastrophic error. bail.
            raise IngestApiError.apiRequestError(ex, self.provider)
        except Exception as error:
            traceback.print_exc()
            raise IngestApiError.apiGeneralError(error, self.provider)

        if response.status_code == 404:
            raise LookupError('Not found %s' % payload)

        try:
            # workaround for httmock lib
            # return etree.fromstring(response.text.encode('utf-8'))
            return etree.fromstring(response.content)
        except UnicodeEncodeError as error:
            traceback.print_exc()
            raise IngestApiError.apiUnicodeError(error, self.provider)
        except ParseError as error:
            traceback.print_exc()
            raise IngestApiError.apiParseError(error, self.provider)
        except Exception as error:
            traceback.print_exc()
            raise IngestApiError.apiGeneralError(error, self.provider)

    def get_url(self, endpoint):
        """Get API url for given endpoint."""
        return '/'.join([self.URL, endpoint])

    def format_date(self, date):
        """Format date for API usage."""
        return date.strftime(self.DATE_FORMAT)

    def prepare_href(self, href):
        (scheme, netloc, path, params, query, fragment) = urlparse(href)
        new_href = urlunparse((scheme, netloc, path, '', '', ''))
        return '%s?auth_token=%s' % (new_href, self.get_token())
