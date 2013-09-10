"""
Superdesk server app
"""

import flask
import flask.ext.pymongo
import flask.ext.restful
import flask.ext.elasticsearch

from .rest import JSONEncoder

app = flask.Flask(__name__)
app.config.from_object('settings')
app.json_encoder = JSONEncoder

mongo = flask.ext.pymongo.PyMongo(app)
api = flask.ext.restful.Api(app)
search = flask.ext.elasticsearch.ElasticSearch(app)

from . import items
from . import auth
from . import elastic

api.add_resource(elastic.ItemListResource, '/items')
#api.add_resource(items.ItemListResource, '/items')
api.add_resource(items.ItemResource, '/items/<string:guid>', endpoint='item')
api.add_resource(auth.AuthResource, '/auth')
