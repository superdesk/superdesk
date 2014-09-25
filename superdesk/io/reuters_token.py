"""Reuters Token Provider"""

import ssl
import requests
import superdesk
from datetime import timedelta
from requests.packages.urllib3.poolmanager import PoolManager
from superdesk.etree import etree
from superdesk.utc import utcnow


def is_valid_token(token):
    ttl = timedelta(hours=12)
    return token.get('created') + ttl >= utcnow()


def update_provider_token(provider):
    """Update provider token."""
    token = {}
    token['token'] = fetch_token_from_api(provider)
    token['created'] = utcnow()
    provider['token'] = token
    superdesk.get_resource_service('ingest_providers').patch(provider['_id'], {'token': token})
    return token['token']


def get_token(provider, update=False):
    """Get auth token for given provider instance and save it in db."""
    token = provider.get('token')
    if token and (is_valid_token(token) or not update):
        return token.get('token')
    return update_provider_token(provider) if update else ''


def fetch_token_from_api(provider):
    session = requests.Session()
    session.mount('https://', SSLAdapter())

    url = 'https://commerce.reuters.com/rmd/rest/xml/login'
    payload = {
        'username': provider.get('config', {}).get('username', ''),
        'password': provider.get('config', {}).get('password', ''),
    }

    response = session.get(url, params=payload, stream=False, verify=False)
    # workaround for httmock lib
    # tree = etree.fromstring(response.text)
    tree = etree.fromstring(response.content)
    return tree.text


# workaround for ssl version error
class SSLAdapter(requests.adapters.HTTPAdapter):
    """SSL Adapter set for ssl tls v1."""

    def init_poolmanager(self, connections, maxsize, **kwargs):
        """Init poolmanager to use ssl version v1."""
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            ssl_version=ssl.PROTOCOL_TLSv1,
            **kwargs
        )
