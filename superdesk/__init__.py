"""
Superdesk server app
"""

import logging
import blinker
import importlib
import settings
import eve.io
import eve.io.elastic
import eve.io.mongo
from flask import abort, app, json, Blueprint  # noqa
from flask.ext.script import Command, Option  # noqa
from eve.utils import document_link, config, ParsedRequest  # noqa

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


class SuperdeskDataLayer(eve.io.DataLayer):
    """Superdesk Data Layer"""

    serializers = eve.io.mongo.Mongo.serializers
    serializers.update(eve.io.elastic.Elastic.serializers)

    def init_app(self, app):
        self.elastic = eve.io.elastic.Elastic(app)
        self.mongo = eve.io.mongo.Mongo(app)
        self.storage = self.mongo.driver
        self._init_elastic()

    def _init_elastic(self):
        """Put elasticsearch mapping."""
        # todo(petr): create a command to set mapping and use domain for mapping
        for typename in ('archive', 'ingest'):
            mapping = {}
            mapping[typename] = {'properties': {
                'uri': {'type': 'string', 'index': 'not_analyzed'},
                'guid': {'type': 'string', 'index': 'not_analyzed'},
                'firstcreated': {'type': 'date'},
                'versioncreated': {'type': 'date'},
                'subject': {
                    'properties': {
                        'name': {'type': 'string', 'index': 'not_analyzed'}
                    }
                }
            }}

            self.elastic.es.put_mapping(self.elastic.index, typename, mapping)

    def find(self, resource, req):
        cursor = self._backend(resource).find(resource, req)
        if not cursor.count():
            return cursor  # return 304 if not modified
        else:
            # but fetch without filter if there is a change
            req.if_modified_since = None
            return self._backend(resource).find(resource, req)

    def find_all(self, resource, max_results=1000):
        req = ParsedRequest()
        req.max_results = max_results
        return self._backend(resource).find(resource, req)

    def find_one(self, resource, **lookup):
        return self._backend(resource).find_one(resource, **lookup)

    def find_list_of_ids(self, resource, ids, client_projection=None):
        return self._backend(resource).find_list_of_ids(resource, ids, client_projection)

    def insert(self, resource, docs, **kwargs):
        self._send('create', resource, docs=docs)
        return self._backend(resource).insert(resource, docs, **kwargs)

    def update(self, resource, id_, updates):
        self._send('update', resource, id=id_, updates=updates)
        return self._backend(resource).update(resource, id_, updates)

    def replace(self, resource, id_, document):
        self._send('update', resource, id=id_, updates=document)
        return self._backend(resource).replace(resource, id_, document)

    def remove(self, resource, id_=None):
        self._send('delete', resource, id_=id_)
        return self._backend(resource).remove(resource, id_)

    def _backend(self, resource):
        datasource, filter_, projection_, sort_ = self._datasource(resource)
        backend = config.SOURCES[datasource].get('backend', 'mongo')
        return getattr(self, backend)

    def _send(self, signal, resource, **kwargs):
        send(signal, self, resource=resource, **kwargs)
        send('%s:%s' % (signal, resource), self, **kwargs)

for app_name in getattr(settings, 'INSTALLED_APPS'):
    importlib.import_module(app_name)
