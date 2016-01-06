# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import datetime
import traceback

import requests
from flask import current_app as app

from superdesk.errors import IngestApiError
from superdesk.etree import etree, ParseError
from superdesk.io import register_feeding_service
from superdesk.io.feeding_services.http_service import HTTPFeedingService
from superdesk.logging import logger
from superdesk.utc import utcnow
from urllib.parse import urlparse, urlunparse


class ReutersHTTPFeedingService(HTTPFeedingService):
    """
    Feeding Service class which can read article(s) using HTTP provided by Reuters.
    """

    NAME = 'reuters_http'

    ERRORS = [IngestApiError.apiTimeoutError().get_error_description(),
              IngestApiError.apiRedirectError().get_error_description(),
              IngestApiError.apiRequestError().get_error_description(),
              IngestApiError.apiUnicodeError().get_error_description(),
              IngestApiError.apiParseError().get_error_description(),
              IngestApiError.apiGeneralError().get_error_description()]

    DATE_FORMAT = '%Y.%m.%d.%H.%M'

    def _update(self, provider):
        updated = utcnow()

        last_updated = provider.get('last_updated')
        ttl_minutes = app.config['INGEST_EXPIRY_MINUTES']
        if not last_updated or last_updated < updated - datetime.timedelta(minutes=ttl_minutes):
            last_updated = updated - datetime.timedelta(minutes=ttl_minutes)

        self.provider = provider
        provider_config = provider.get('config')
        if not provider_config:
            provider_config = {}
            provider['config'] = provider_config

        if 'url' not in provider_config:
            provider_config['url'] = 'http://rmb.reuters.com/rmd/rest/xml'

        if 'auth_url' not in provider_config:
            provider_config['auth_url'] = 'https://commerce.reuters.com/rmd/rest/xml/login'

        self.URL = provider_config.get('url')

        for channel in self._get_channels():
            for guid in self._get_article_ids(channel, last_updated, updated):
                items = self.fetch_ingest(guid)
                if items:
                    yield items

    def _get_channels(self):
        """Get subscribed channels."""
        channels = []
        tree = self._get_tree('channels')
        for channel in tree.findall('channelInformation'):
            channels.append(channel.find('alias').text)

        return channels

    def _get_tree(self, endpoint, payload=None):
        """
        Get xml response for given API endpoint and payload.
        :param: endpoint
        :type endpoint: str
        :param: payload
        :type payload: str
        """

        if payload is None:
            payload = {}

        payload['token'] = self._get_auth_token(self.provider, update=True)
        url = self._get_absolute_url(endpoint)

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
            return etree.fromstring(response.content)  # workaround for http mock lib
        except UnicodeEncodeError as error:
            traceback.print_exc()
            raise IngestApiError.apiUnicodeError(error, self.provider)
        except ParseError as error:
            traceback.print_exc()
            raise IngestApiError.apiParseError(error, self.provider)
        except Exception as error:
            traceback.print_exc()
            raise IngestApiError.apiGeneralError(error, self.provider)

    def _get_absolute_url(self, endpoint):
        """
        Get absolute URL for given endpoint.

        :param: endpoint
        :type endpoint: str
        """
        return '/'.join([self.URL, endpoint])

    def _get_article_ids(self, channel, last_updated, updated):
        """
        Get article ids which should be upserted.
        """

        ids = set()
        payload = {'channel': channel, 'fieldsRef': 'id',
                   'dateRange': "%s-%s" % (self._format_date(last_updated), self._format_date(updated))}

        logger.info('Reuters requesting Date Range |{}| for channel {}'.format(payload['dateRange'], channel))
        tree = self._get_tree('items', payload)
        for result in tree.findall('result'):
            ids.add(result.find('guid').text)

        return ids

    def _format_date(self, date):
        return date.strftime(self.DATE_FORMAT)

    def fetch_ingest(self, guid):
        items = self._parse_items(guid)
        result_items = []
        while items:
            item = items.pop()
            self.add_timestamps(item)
            try:
                items.extend(self._fetch_items_in_package(item))
                result_items.append(item)
            except LookupError as err:
                self.log_item_error(err, item, self.provider)
                return []

        return result_items

    def _parse_items(self, guid):
        """
        Parse item message and return given items.
        """

        payload = {'id': guid}
        tree = self._get_tree('item', payload)

        parser = self.get_feed_parser(self.provider, tree)
        items = parser.parse(tree, self.provider)

        return items

    def _fetch_items_in_package(self, item):
        """
        Fetch remote assets for given item.
        """
        items = []
        for group in item.get('groups', []):
            for ref in group.get('refs', []):
                if 'residRef' in ref:
                    items.extend(self._parse_items(ref.get('residRef')))

        return items

    def prepare_href(self, href):
        (scheme, netloc, path, params, query, fragment) = urlparse(href)
        new_href = urlunparse((scheme, netloc, path, '', '', ''))
        return '%s?auth_token=%s' % (new_href, self._get_auth_token(self.provider, update=True))


register_feeding_service(ReutersHTTPFeedingService.NAME, ReutersHTTPFeedingService(), ReutersHTTPFeedingService.ERRORS)
