"""
Superdesk server app
"""

import importlib

import flask
import flask.ext.restful
import flask.ext.elasticsearch
import flask.ext.script

from superdesk.api import JSONEncoder

app = flask.Flask(__name__)
app.config.from_object('settings')
app.json_encoder = JSONEncoder

api = flask.ext.restful.Api(app)
search = flask.ext.elasticsearch.ElasticSearch(app)
manager = flask.ext.script.Manager(app)

with app.app_context():
    for app_name in app.config.get('INSTALLED_APPS', []):
        importlib.import_module(app_name)
