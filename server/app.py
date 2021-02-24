#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
import settings

from superdesk.factory import get_app as superdesk_app
from ansa.vfs import VFSMediaStorage
from elasticapm.contrib.flask import ElasticAPM


media_storage = None
if os.environ.get('ANSA_VFS'):
    media_storage = VFSMediaStorage


def get_app(config=None, init_elastic=False):
    """App factory.

    :param config: configuration that can override config from `settings.py`
    :return: a new SuperdeskEve app instance
    """
    if config is None:
        config = {}

    config['APP_ABSPATH'] = os.path.abspath(os.path.dirname(__file__))

    for key in dir(settings):
        if key.isupper():
            config.setdefault(key, getattr(settings, key))

    app = superdesk_app(config, media_storage=media_storage)

    if os.environ.get('APM_SERVER_URL') and os.environ.get('APM_SECRET_TOKEN'):
        app.config['ELASTIC_APM'] = {
            'DEBUG': app.debug,
            'TRANSACTIONS_IGNORE_PATTERNS': ['^OPTIONS '],
            'SERVER_URL': os.environ['APM_SERVER_URL'],
            'SECRET_TOKEN': os.environ['APM_SECRET_TOKEN'],
            'SERVICE_NAME': os.environ.get('APM_SERVICE_NAME') or 'superdesk',
        }

        ElasticAPM(app)

    return app


if __name__ == '__main__':
    debug = True
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', '5000'))
    app = get_app()
    app.run(host=host, port=port, debug=debug, use_reloader=debug)
