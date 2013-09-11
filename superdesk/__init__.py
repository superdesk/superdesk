"""
Superdesk server app
"""

import importlib

import flask
import flask.ext.pymongo
import flask.ext.restful
import flask.ext.elasticsearch
import flask.ext.script

from .rest import JSONEncoder

app = flask.Flask(__name__)
app.config.from_object('settings')
app.json_encoder = JSONEncoder

api = flask.ext.restful.Api(app)
mongo = flask.ext.pymongo.PyMongo(app)
search = flask.ext.elasticsearch.ElasticSearch(app)
manager = flask.ext.script.Manager(app)

for app_name in app.config.get('INSTALLED_APPS', []):
    importlib.import_module(app_name)
