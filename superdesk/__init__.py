"""
Superdesk server app
"""

import blinker
import importlib
import eve.io.mongo
import settings
from flask import abort

def connect(signal, subscriber):
    """Connect to signal."""
    blinker.signal(signal).connect(subscriber)

def send(signal, *sender, **kwargs):
    """Send signal."""
    send_sender = sender[0] if sender else None
    blinker.signal(signal).send(send_sender, **kwargs)

class SuperdeskData(eve.io.mongo.Mongo):
    """Superdesk Data Layer"""

    def insert(self, resource, docs):
        """Insert documents into resource storage."""
        send('insert', self, resource=resource, docs=docs)
        send('insert:%s' % resource, self, docs=docs)
        return super(SuperdeskData, self).insert(resource, docs)

db = None
DOMAIN = {}

for app_name in settings.INSTALLED_APPS:
    importlib.import_module(app_name)
