"""Reuters Token Provider"""

import os
import ssl
import requests
import xml.etree.ElementTree as etree
from requests.packages.urllib3.poolmanager import PoolManager
from datetime import datetime, timedelta

import superdesk
from superdesk.utc import utcnow

PROVIDER = 'reuters'

def is_valid_token(token):
    ttl = timedelta(hours=12)
    return token.get('created') + ttl >= utcnow()

def get_token(db):
    token = db.find_one('tokens', provider=PROVIDER)
    if token and is_valid_token(token):
        return token.get('token')
    elif token:
        db.remove('tokens', token.get('_id'))

    token = {
        'provider': PROVIDER,
        'token': fetch_token_from_api(),
        'created': datetime.utcnow(),
    }

    db.insert('tokens', token)
    return token.get('token')

def fetch_token_from_api():
    session = requests.Session()
    session.mount('https://', SSLAdapter())

    url = 'https://commerce.reuters.com/rmd/rest/xml/login'
    payload = {
        'username': os.environ.get('REUTERS_USERNAME', ''),
        'password': os.environ.get('REUTERS_PASSWORD', ''),
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
