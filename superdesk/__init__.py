"""Superdesk"""

import logging
import settings
import importlib
from flask import abort, json, Blueprint  # noqa
from flask.ext.script import Command, Option  # noqa @UnresolvedImport
from eve.methods.common import document_link  # noqa
from .datalayer import SuperdeskDataLayer  # noqa
from .signals import connect, send  # noqa
from werkzeug.exceptions import HTTPException

app = None
API_NAME = 'Superdesk API'
VERSION = (0, 0, 1)
DOMAIN = {}
COMMANDS = {}
BLUEPRINTS = []

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SuperdeskError(Exception):
    """Base error class for superdesk."""

    # default error status code
    status_code = 400

    def __init__(self, message=None, status_code=None, payload=None):
        """
        :param message: a human readable error description
        :param status_code: response status code
        :param payload: a dict with request issues
        """
        Exception.__init__(self)
        self.message = message

        if status_code is not None:
            self.status_code = status_code

        if payload is not None:
            self.payload = payload

    def to_dict(self):
        """Create dict for json response."""
        rv = {}
        rv[app.config['STATUS']] = app.config['STATUS_ERR']
        rv[app.config['ISSUES']] = dict(self.payload or ())
        rv['_message'] = self.message or ''
        return rv


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


def domain(resource, config):
    """Register domain resource"""
    DOMAIN[resource] = config


def command(name, command):
    """Register command"""
    COMMANDS[name] = command


def blueprint(blueprint, **kwargs):
    """Register blueprint"""
    blueprint.kwargs = kwargs
    BLUEPRINTS.append(blueprint)


for app_name in getattr(settings, 'INSTALLED_APPS'):
    importlib.import_module(app_name)
