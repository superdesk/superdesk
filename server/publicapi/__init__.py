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
A module that provides the Superdesk public API application object.

The object is a normal `Flask <http://flask.pocoo.org/>`_ application (or, to
be more specific, an `Eve framework <http://python-eve.org/>`_ application).
"""

from eve import Eve
from eve.io.mongo.mongo import MongoJSONEncoder
from eve.render import send_response
import importlib
import logging
import os

from publicapi import settings
import superdesk
from superdesk.datalayer import SuperdeskDataLayer
from superdesk.errors import SuperdeskError, SuperdeskApiError


logger = logging.getLogger('superdesk')


def get_app(config=None):
    """
    App factory.

    :param dict config: configuration that can override config
        from `settings.py`
    :return: a new SuperdeskEve app instance
    """
    if config is None:
        config = {}

    config['APP_ABSPATH'] = os.path.abspath(os.path.dirname(__file__))
    for key in dir(settings):
        if key.isupper():
            config.setdefault(key, getattr(settings, key))

    app = Eve(
        settings=config,
        data=SuperdeskDataLayer,
        json_encoder=MongoJSONEncoder,
    )

    superdesk.app = app

    @app.errorhandler(SuperdeskError)
    def client_error_handler(error):
        """Return json error response.

        :param error: an instance of :attr:`superdesk.SuperdeskError` class
        """
        return send_response(None, (error.to_dict(), None, None, error.status_code))

    @app.errorhandler(500)
    def server_error_handler(error):
        """Log server errors."""
        app.sentry.captureException()
        logger.exception(error)
        return_error = SuperdeskApiError.internalError()
        return client_error_handler(return_error)

    for module_name in app.config['INSTALLED_APPS']:
        app_module = importlib.import_module(module_name)
        try:
            app_module.init_app(app)
        except AttributeError:
            pass

    for resource in config['DOMAIN']:
        app.register_resource(resource, config['DOMAIN'][resource])

    return app
