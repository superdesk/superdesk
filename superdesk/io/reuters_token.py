"""Reuters Token Provider"""

import os
import ssl
import requests
from requests.packages.urllib3.poolmanager import PoolManager
import xml.etree.ElementTree as etree

class ReutersTokenProvider(object):

    token = None

    def get_token(self):
        """Get access token."""

        if self.token:
            return self.token

        session = requests.Session()
        session.mount('https://', SSLAdapter())

        url = 'https://commerce.reuters.com/rmd/rest/xml/login'
        payload = {
            'username': os.environ.get('REUTERS_USERNAME', ''),
            'password': os.environ.get('REUTERS_PASSWORD', ''),
        }

        response = session.get(url, params=payload)
        tree = etree.fromstring(response.text)
        self.token = tree.text
        return self.token

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
