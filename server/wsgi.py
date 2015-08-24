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
import threading
from werkzeug.wsgi import pop_path_info, peek_path_info
from app import get_app
from superdesk.logging import logger


class PathDispatcher(object):

    def __init__(self, create_app):
        self.create_app = create_app
        self.lock = threading.Lock()
        self.instances = {}

    def get_application(self, prefix):
        if prefix == 'api':
            raise ValueError(prefix)
        with self.lock:
            app = self.instances.get(prefix)
            if app is None:
                app = self.create_app(prefix=prefix)
                self.instances[prefix] = app
            return app

    def __call__(self, environ, start_response):
        try:
            app = self.get_application(peek_path_info(environ))
            pop_path_info(environ)
            return app(environ, start_response)
        except ValueError:
            logger.error('api req: %s' % (environ, ))
            raise

if os.environ.get('SUPERDESK_TESTING'):
    application = PathDispatcher(get_app)
else:
    application = get_app()
