# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Superdesk"""

import logging
from flask import abort, json, Blueprint, current_app as app  # noqa
from flask.ext.script import Command as BaseCommand, Option  # noqa @UnresolvedImport
from werkzeug.exceptions import HTTPException
from eve.utils import config  # noqa
from eve.methods.common import document_link  # noqa

from .eve_backend import EveBackend
from .datalayer import SuperdeskDataLayer  # noqa
from .services import BaseService as Service  # noqa
from .resource import Resource  # noqa
from .privilege import privilege, intrinsic_privilege, get_intrinsic_privileges  # noqa
from .workflow import *  # noqa


API_NAME = 'Superdesk API'
VERSION = (0, 0, 1)
DOMAIN = {}
COMMANDS = {}
BLUEPRINTS = []
app_components = dict()
app_models = dict()
resources = dict()
eve_backend = EveBackend()
default_user_preferences = dict()
default_session_preferences = dict()


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    The Eve framework changes introduced with https://github.com/nicolaiarocci/eve/issues/213 make the commands fail.
    Reason being the flask-script's run the commands using test_request_context() which is invalid.
    That's the reason we are inheriting the Flask-Script's Command to overcome this issue.
    """

    def __call__(self, _app=None, *args, **kwargs):
        try:
            with app.app_context():
                res = self.run(*args, **kwargs)
                print('Command finished with: ', res)
                return 0
        except Exception as ex:
            print('Uhoh, an exception occured while running the command...')
            logger.exception(ex)
            return 1


def get_headers(self, environ=None):
    """Fix CORS for abort responses.

    todo(petr): put in in custom flask error handler instead
    """
    return [
        ('Content-Type', 'text/html'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Headers', '*'),
    ]

setattr(HTTPException, 'get_headers', get_headers)


def domain(resource, res_config):
    """Register domain resource"""
    DOMAIN[resource] = res_config


def command(name, command):
    """Register command"""
    COMMANDS[name] = command


def blueprint(blueprint, **kwargs):
    """Register blueprint"""
    blueprint.kwargs = kwargs
    BLUEPRINTS.append(blueprint)


def get_backend():
    """Returns the available backend, this will be changed in a factory if needed."""
    return eve_backend


def get_resource_service(resource_name):
    return resources[resource_name].service


def get_resource_privileges(resource_name):
    attr = getattr(resources[resource_name], 'privileges', {})
    return attr


def register_default_user_preference(preference_name, preference):
    default_user_preferences[preference_name] = preference


def register_default_session_preference(preference_name, preference):
    default_session_preferences[preference_name] = preference
