"""
Superdesk server app
"""

import blinker
import importlib
import eve.io.mongo
import settings

def connect(signal, subscriber):
    blinker.signal(signal).connect(subscriber)

def send(signal, *sender, **kwargs):
    blinker.signal(signal).send(sender, **kwargs)

class Superdesk(eve.io.mongo.Mongo):

    def insert(self, resource, doc_or_docs):
        data = super(Superdesk, self).insert(resource, doc_or_docs)
        send('insert', resource=resource, docs=doc_or_docs)
        return data

db = None
DOMAIN = {}

for app_name in settings.INSTALLED_APPS:
    importlib.import_module(app_name)
