"""
Superdesk server app
"""

import logging
import blinker
import importlib
import eve.io.mongo
import settings
from flask import abort, app, Blueprint, json
from flask.ext.script import Command, Option
from eve.utils import document_link

API_NAME = 'Superdesk API'
VERSION = (0, 0, 1)
DOMAIN = {}
COMMANDS = {}
BLUEPRINTS = []

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def connect(signal, subscriber):
    """Connect to signal"""
    blinker.signal(signal).connect(subscriber)

def send(signal, sender, **kwargs):
    """Send signal"""
    blinker.signal(signal).send(sender, **kwargs)

def proxy_resource_signal(action, app):
    def handle(resource, documents):
        send(action, app.data, docs=documents)
        send('%s:%s' % (action, resource), app.data, docs=documents)
    return handle

def proxy_item_signal(action, app):
    def handle(resource, id, document):
        send(action, app.data, resource=resource, docs=[document])
        send('%s:%s' % (action, resource), app.data, docs=[document])
    return handle

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

def get_db():
    """Get db"""
    return app.data.driver.db

class SuperdeskData(eve.io.mongo.Mongo):
    """Superdesk Data Layer"""

    def _send(self, signal, resource, docs):
        send(signal, self, resource=resource, docs=docs)
        send('%s:%s' % (signal, resource), self, docs=docs)

    def insert(self, resource, docs):
        """Insert documents into resource storage."""
        self._send('create', resource, docs)
        return super(SuperdeskData, self).insert(resource, docs)

for app_name in getattr(settings, 'INSTALLED_APPS'):
    importlib.import_module(app_name)
