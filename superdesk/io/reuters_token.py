"""Reuters Token Provider"""

import ssl
import requests
import xml.etree.ElementTree as etree
from requests.packages.urllib3.poolmanager import PoolManager
from datetime import datetime, timedelta

import superdesk
from superdesk.utc import utcnow

def is_valid_token(token):
    ttl = timedelta(hours=12)
    return token.get('created') + ttl >= utcnow()

def get_token(provider):
    token = provider.get('token')
    if token and is_valid_token(token):
        return token.get('token')

    token = {
        'token': fetch_token_from_api(provider),
        'created': utcnow(),
    }

    provider['token'] = token

    db = superdesk.get_db()
    db['ingest_providers'].save(provider)
    return token.get('token')

def fetch_token_from_api(provider):
    session = requests.Session()
    session.mount('https://', SSLAdapter())

    url = 'https://commerce.reuters.com/rmd/rest/xml/login'
    payload = {
        'username': provider.get('config', {}).get('username', ''),
        'password': provider.get('config', {}).get('password', ''),
    }

    response = session.get(url, params=payload)
    tree = etree.fromstring(response.text)
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
