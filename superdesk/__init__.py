"""
Superdesk server app
"""

import flask
import flask.ext.restful
import flask.ext.pymongo
from bson.objectid import ObjectId
from datetime import datetime

class MyJSONEncoder(flask.json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)

        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%S%z')

        super(MyJSONEncoder, self).default(o)

app = flask.Flask('superdesk')
app.config.from_object('settings')
app.json_encoder = MyJSONEncoder

mongo = flask.ext.pymongo.PyMongo(app)

import items
import auth

api = flask.ext.restful.Api(app)
api.add_resource(items.ItemListResource, '/items')
api.add_resource(items.ItemResource, '/items/<string:guid>')
api.add_resource(auth.AuthResource, '/auth')

@api.representation('application/json')
def to_json(data, code, headers=None):
    dump = flask.json.dumps(data) if data else ''
    resp = flask.make_response(dump, code)
    resp.headers.extend(headers or {})

    if 'Access-Control-Allow-Origin' not in resp.headers:
        resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp
