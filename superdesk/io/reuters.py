"""Reuters io service."""

import requests
import xml.etree.ElementTree as etree
import traceback
import datetime

from superdesk.datetime import utcnow
from superdesk.items import save_item, get_last_updated, ItemConflictException

class ReutersService(object):
    """Update Service"""

    URL = 'http://rmb.reuters.com/rmd/rest/xml'
    DATE_FORMAT = '%Y.%m.%d.%H.%M'

    def __init__(self, parser, tokenProvider):
        self.parser = parser
        self.tokenProvider = tokenProvider

    def get_token(self):
        return self.tokenProvider.get_token()

    def update(self):
        """Service update call."""

        updated = utcnow()
        last_updated = get_last_updated()
        if not last_updated or last_updated < updated + datetime.timedelta(days=-7):
            last_updated = updated + datetime.timedelta(hours=-12) # last 12h

        for channel in self.get_channels():
            for guid in self.get_ids(channel, last_updated, updated):
                items = self.get_items(guid)
                self.save_items(items)

    def save_items(self, items):
        items.reverse()
        for item in items:
            self.fetch_assets(item)
            try:
                save_item(item)
            except ItemConflictException:
                pass

    def fetch_assets(self, item):
        """Fetch remote assets for given item."""
        for group in item.get('groups', []):
            for ref in group.get('refs', []):
                if 'residRef' in ref:
                    items = self.get_items(ref.get('residRef'))
                    self.save_items(items)

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
        payload['dateRange'] = "%s-%s" % (self.format_date(last_updated),
                self.format_date(updated))
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
            response = requests.get(url, params=payload, timeout=5.0)
        except Exception as error:
            traceback.print_exc()
            raise error

        try:
            return etree.fromstring(response.text.encode('utf-8'))
        except UnicodeEncodeError as error:
            traceback.print_exc()
            raise error

    def get_url(self, endpoint):
        """Get API url for given endpoint."""
        return '/'.join([self.URL, endpoint])

    def format_date(self, date):
        """Format date for API usage."""
        return date.strftime(self.DATE_FORMAT)

