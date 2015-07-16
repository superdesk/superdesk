# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""
A module containing configuration of the Superdesk's public API.

The meaning of configuration options is described in the Eve framework
`documentation <http://python-eve.org/config.html#global-configuration>`_.
"""

import os
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def env(variable, fallback_value=None):
    env_value = os.environ.get(variable, '')
    if len(env_value) == 0:
        return fallback_value
    else:
        if env_value == "__EMPTY__":
            return ''
        else:
            return env_value

PUBLICAPI_MONGO_DBNAME = 'publicapi'
PUBLICAPI_MONGO_URI = os.environ.get(
    'PUBLICAPI_MONGO_URI',
    'mongodb://localhost/' + PUBLICAPI_MONGO_DBNAME)

INSTALLED_APPS = [
    'publicapi.items',
    'publicapi.packages',
    'publicapi.prepopulate',
    'publicapi.assets'
]

DOMAIN = {}

SUPERDESK_PUBLICAPI_TESTING = False

# NOTE: no trailing slash for the PUBLICAPI_URL setting!
PUBLICAPI_URL = env('PUBLICAPI_URL', 'http://localhost:5050')
server_url = urlparse(PUBLICAPI_URL)
SERVER_NAME = server_url.netloc or None
URL_PROTOCOL = server_url.scheme or None
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

# Amazon S3 assets management
AMAZON_CONTAINER_NAME = env('AMAZON_CONTAINER_NAME', '')
AMAZON_ACCESS_KEY_ID = env('AMAZON_ACCESS_KEY_ID', '')
AMAZON_SECRET_ACCESS_KEY = env('AMAZON_SECRET_ACCESS_KEY', '')
AMAZON_REGION = env('AMAZON_REGION', 'us-east-1')
AMAZON_SERVE_DIRECT_LINKS = env('AMAZON_SERVE_DIRECT_LINKS', False)
AMAZON_S3_USE_HTTPS = env('AMAZON_S3_USE_HTTPS', False)
