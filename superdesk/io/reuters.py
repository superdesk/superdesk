"""Reuters io service."""

import requests
import traceback
import datetime
import superdesk

from superdesk.utc import utcnow
from superdesk.utc import utc
from superdesk.etree import etree
from urllib.parse import urlparse, urlunparse
from superdesk.io import register_provider, IngestService
from .newsml_2_0 import Parser
from .reuters_token import get_token


PROVIDER = 'reuters'


class ReutersIngestService(IngestService):
    """Reuters ingest service."""

    DATE_FORMAT = '%Y.%m.%d.%H.%M'
    URL = 'http://rmb.reuters.com/rmd/rest/xml'
    token = None

    def __init__(self):
        self.parser = Parser()

    def get_token(self):
        """Get reuters token once for an update run."""

        if not self.token:
            self.token = get_token(self.provider, update=True)
        return self.token

    def update(self, provider):
        """Service update call."""

        self.provider = provider
        updated = utcnow()

        last_updated = provider.get('_updated')
        if not last_updated or last_updated < updated + datetime.timedelta(days=-7):
            last_updated = updated + datetime.timedelta(hours=-24)

        for channel in self.get_channels():
            for guid in self.get_ids(channel, last_updated, updated):
                items = self.fetch_ingest(guid)
                yield items

    def fetch_ingest(self, guid):
        items = self.get_items(guid)
        result_items = []
        while items:
            item = items.pop()
            result_items.append(item)
            item['_created'] = item['firstcreated'] = utc.localize(item['firstcreated'])
            item['_updated'] = item['versioncreated'] = utc.localize(item['versioncreated'])
            items.extend(self.fetch_assets(item))
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
        items = self.parser.parse_message(tree)
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
            response = requests.get(url, params=payload, timeout=21.0)
        except Exception as error:
            traceback.print_exc()
            raise error

        if response.status_code == 404:
            raise LookupError('Not found %s' % payload)

        try:
            # workaround for httmock lib
            # return etree.fromstring(response.text.encode('utf-8'))
            return etree.fromstring(response.content)
        except UnicodeEncodeError as error:
            traceback.print_exc()
            raise error

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


def on_read_ingest(data, docs):
    provider = data.find_one('ingest_providers', type=PROVIDER, req=None)
    if not provider:
        return
    for doc in docs:
        if str(doc.get('ingest_provider')) == str(provider['_id']):
            for i, rendition in doc.get('renditions', {}).items():
                rendition['href'] = '%s?auth_token=%s' % (rendition['href'], get_token(provider))


superdesk.connect('read:ingest', on_read_ingest)
register_provider(PROVIDER, ReutersIngestService())
