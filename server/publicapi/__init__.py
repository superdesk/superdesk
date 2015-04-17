# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from flask.globals import current_app
"""
A module that provides the Superdesk public API application object.

The object is a normal `Flask <http://flask.pocoo.org/>`_ application (or, to
be more specific, an `Eve framework <http://python-eve.org/>`_ application).
"""

from eve import Eve
from eve.io.mongo.mongo import MongoJSONEncoder
import importlib
import os

from publicapi import settings
import superdesk
from superdesk.datalayer import SuperdeskDataLayer


def get_app(config=None):
    """App factory.

    :param config: configuration that can override config from `settings.py`
    :return: a new SuperdeskEve app instance
    """
    if config is None:
        config = {}

    for key in dir(settings):
        if key.isupper():
            config.setdefault(key, getattr(settings, key))

    app = Eve(
        settings=config,
        data=SuperdeskDataLayer,
        json_encoder=MongoJSONEncoder,
    )

    superdesk.app = app

    for module_name in app.config['INSTALLED_APPS']:
        app_module = importlib.import_module(module_name)
        try:
            app_module.init_app(app)
        except AttributeError:
            pass

    for resource in config['DOMAIN']:
        app.register_resource(resource, config['DOMAIN'][resource])

    return app
