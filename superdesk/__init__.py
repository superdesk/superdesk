"""
Superdesk server app
"""

import flask
import flask.ext.pymongo
import flask.ext.restful

from .rest import JSONEncoder

app = flask.Flask(__name__)
app.config.from_object('settings')
app.json_encoder = JSONEncoder

mongo = flask.ext.pymongo.PyMongo(app)

api = flask.ext.restful.Api(app)

from . import items
from . import auth

api.add_resource(items.ItemListResource, '/items')
api.add_resource(items.ItemResource, '/items/<string:guid>')
api.add_resource(auth.AuthResource, '/auth')
