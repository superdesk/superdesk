# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import feedparser
import requests

from calendar import timegm
from collections import namedtuple
from datetime import datetime

from superdesk.errors import IngestApiError, ParserError
from superdesk.io import register_provider
from superdesk.io.ingest_service import IngestService
from superdesk.utils import merge_dicts


PROVIDER = 'rss'

utcfromtimestamp = datetime.utcfromtimestamp

errors = [IngestApiError.apiAuthError().get_error_description(),
          IngestApiError.apiNotFoundError().get_error_description(),
          IngestApiError.apiGeneralError().get_error_description(),
          ParserError.parseMessageError().get_error_description()]


class RssIngestService(IngestService):
    """Ingest service for providing feeds received in RSS 2.0 format.

    (NOTE: it should also work with other syndicated feeds formats, too, since
    the underlying parser supports them, but for our needs RSS 2.0 is assumed)
    """

    ItemField = namedtuple('ItemField', ['name', 'name_in_data', 'type'])

    item_fields = [
        ItemField('guid', 'guid', str),
        ItemField('uri', 'guid', str),
        ItemField('firstcreated', 'published_parsed', datetime),
        ItemField('versioncreated', 'updated_parsed', datetime),
        ItemField('headline', 'title', str),
        ItemField('abstract', 'summary', str),
        ItemField('body_html', 'body_text', str),
    ]
    """A list of fields that items created from the ingest data should contain.

    Each list item is a named tuple with the following three attribues:

    * name - the name of the field (attribute) in the resulting ingest item
    * name_in_data - the expected name of the data field in the retrieved
        ingest data (this can be overriden by providing a field name alias)
    * type - field's data type
    """

    def _update(self, provider):
        """Check data provider for data updates and returns new items (if any).

        :param provider: data provider instance
        :return: a list containing a list of new content items
        :rtype: list

        :raises IngestApiError: if data retrieval error occurs
        :raises ParserError: if retrieved RSS data cannot be parsed
        """
        config = provider.get('config', {})

        try:
            xml_data = self._fetch_data(config, provider)
            data = feedparser.parse(xml_data)
        except IngestApiError:
            raise
        except Exception as ex:
            raise ParserError.parseMessageError(ex, provider)

        # If provider last updated time is not available, set it to 1.1.1970
        # so that it will be recognized as "not up to date".
        # Also convert it to a naive datetime object (removing tzinfo is fine,
        # because it is in UTC anyway)
        t_provider_updated = provider.get('last_updated', utcfromtimestamp(0))
        t_provider_updated = t_provider_updated.replace(tzinfo=None)

        new_items = []
        field_aliases = config.get('field_aliases')

        for entry in data.entries:
            t_entry_updated = utcfromtimestamp(timegm(entry.updated_parsed))

            if t_entry_updated > t_provider_updated:
                item = self._create_item(entry, field_aliases)
                self.add_timestamps(item)
                new_items.append(item)

        return [new_items]

    def _fetch_data(self, config, provider):
        """Fetch the latest feed data.

        :param dict config: RSS resource configuration
        :param provider: data provider instance
        :return: fetched RSS data
        :rtype: str

        :raises IngestApiError: if fetching data fails for any reason
            (e.g. authentication error, resource not found, etc.)
        """
        url = config['url']

        if config.get('auth_required', False):
            auth = (config.get('username'), config.get('password'))
        else:
            auth = None

        response = requests.get(url, auth=auth)

        if response.ok:
            return response.content
        else:
            if response.status_code in (401, 403):
                raise IngestApiError.apiAuthError(
                    Exception(response.reason), provider)
            elif response.status_code == 404:
                raise IngestApiError.apiNotFoundError(
                    Exception(response.reason), provider)
            else:
                raise IngestApiError.apiGeneralError(
                    Exception(response.reason), provider)

    def _create_item(self, data, field_aliases=None):
        """Create a new content item from RSS feed data.

        :param dict data: parsed data of a single feed entry
        :param field_aliases: (optional) field name aliases. Used for content
             fields that are named differently in retrieved data.
        :type field_aliases: dict or None

        :return: created content item
        :rtype: dict
        """
        if field_aliases is None:
            field_aliases = {}
        else:
            field_aliases = merge_dicts(field_aliases)

        item = dict(type='text')

        for field in self.item_fields:
            data_field_name = field_aliases.get(
                field.name_in_data, field.name_in_data
            )
            field_value = data.get(data_field_name)

            if (field.type is datetime) and field_value:
                field_value = utcfromtimestamp(timegm(field_value))

            item[field.name] = field_value

        return item


register_provider(PROVIDER, RssIngestService(), errors)
