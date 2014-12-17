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
from .privilege import privilege  # noqa
from .workflow import *  # noqa
from eve.validation import ValidationError


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

    def __call__(self, app=None, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


class SuperdeskError(ValidationError):
    """Base error class for superdesk."""

    # default error status code
    status_code = 400

    def __init__(self, message=None, status_code=None, payload=None):
        """
        :param message: a human readable error description
        :param status_code: response status code
        :param payload: a dict with request issues
        """
        ValidationError.__init__(self, message)
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
        if hasattr(self, 'payload'):
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


class InvalidStateTransitionError(SuperdeskError):
    """Exception raised if workflow transition is invalid."""

    def __init__(self, message='Workflow transition is invalid.', status_code=None, payload=None):
        super().__init__(message, status_code, payload)
