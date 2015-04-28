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


MONGO_DBNAME = 'publicapi'

INSTALLED_APPS = [
    'publicapi.items',
    'publicapi.packages',
    'publicapi.prepopulate'
]

DOMAIN = {}

SUPERDESK_PUBLICAPI_TESTING = True

PUBLICAPI_URL = env('PUBLICAPI_URL', 'http://localhost:5050')
server_url = urlparse(PUBLICAPI_URL)
SERVER_NAME = server_url.netloc or None
