"""Superdesk"""

import logging
import settings
import importlib
from flask import abort, json, Blueprint  # noqa
from flask.ext.script import Command, Option  # noqa
from eve.utils import document_link  # noqa
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


def get_headers(self, environ=None):
    """Fix CORS for abort responses."""
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
