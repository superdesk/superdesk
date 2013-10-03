"""
Superdesk server app
"""

import blinker
import importlib
import eve.io.mongo
import settings
from flask import abort, app
from flask.ext.script import Command

VERSION = (0, 0, 1)
DOMAIN = {}
COMMANDS = {}

def get_sender(sender):
    return sender[0] if sender else None

def connect(signal, subscriber):
    """Connect to signal."""
    blinker.signal(signal).connect(subscriber)

def send(signal, *sender, **kwargs):
    """Send signal."""
    blinker.signal(signal).send(get_sender(sender), **kwargs)

def domain(resource, config):
    """Add resource to register"""
    DOMAIN[resource] = config

def command(name, command):
    """Add command to register"""
    COMMANDS[name] = command

def proxy_resource_signal(action, app):
    def handle_signal(resource, documents):
        send(action, app.data, docs=documents)
        send('%s:%s' % (action, resource), app.data, docs=documents)
    return handle_signal

def proxy_item_signal(action, app):
    def handle_signal(resource, id, document):
        send('%s:%s' % (action, resource), app.data, docs=[document])
    return handle_signal

class SuperdeskData(eve.io.mongo.Mongo):
    """Superdesk Data Layer"""

    def insert(self, resource, docs):
        """Insert documents into resource storage."""
        send('create', self, resource=resource, docs=docs)
        send('create:%s' % resource, self, docs=docs)
        return super(SuperdeskData, self).insert(resource, docs)

for app_name in settings.INSTALLED_APPS:
    importlib.import_module(app_name)
