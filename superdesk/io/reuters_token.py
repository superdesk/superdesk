"""Reuters Token Provider"""

import os
import ssl
import requests
import xml.etree.ElementTree as etree
from requests.packages.urllib3.poolmanager import PoolManager
from datetime import datetime, timedelta

import superdesk
from superdesk.datetime import utcnow

class ReutersTokenProvider(object):
    """Provides auth token for reuters api"""

    PROVIDER = 'reuters'

    def __init__(self, db=superdesk.db):
        self.db = db

    def get_token(self):
        """Get access token."""

        token = self.db.tokens.find_one({'provider': self.PROVIDER})
        if token and self.is_valid(token):
            return token.get('token')
        elif token:
            self.db.tokens.remove(token)

        token = {
            'provider': self.PROVIDER,
            'created': datetime.utcnow(),
            'token': fetch_token_from_api(),
        }

        self.db.tokens.save(token)
        return token.get('token')

    def is_valid(self, token):
        ttl = timedelta(hours=12)
        return token.get('created') + ttl >= utcnow()

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

tokenProvider = ReutersTokenProvider()
