"""Superdesk"""

import logging
import settings  # noqa
from flask import abort, json, Blueprint, current_app as app  # noqa
from flask.ext.script import Command, Option  # noqa @UnresolvedImport
from eve.methods.common import document_link  # noqa
from .datalayer import SuperdeskDataLayer  # noqa
from .signals import connect, send  # noqa
from werkzeug.exceptions import HTTPException
from eve.utils import config  # noqa

API_NAME = 'Superdesk API'
VERSION = (0, 0, 1)
DOMAIN = {}
COMMANDS = {}
BLUEPRINTS = []
apps = dict()

logger = logging.getLogger(__name__)


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

        if status_code:
            self.status_code = status_code

        if payload:
            self.payload = payload

    def to_dict(self):
        """Create dict for json response."""
        rv = {}
        rv[app.config['STATUS']] = app.config['STATUS_ERR']
        rv['_message'] = self.message or ''
        if getattr(self, 'payload'):
            rv[app.config['ISSUES']] = self.payload
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
