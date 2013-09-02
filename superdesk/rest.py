"""Superdesk API

Providers base Resource with CORS support and own jsonencoder.
"""

from datetime import datetime

from bson.objectid import ObjectId
from flask import current_app as app
import flask.json
import flask.ext.restful

def to_json(data, code, headers=None):
    dump = flask.json.dumps(data) if data else ''
    resp = flask.make_response(dump, code)
    resp.headers.extend(headers or {})

    if 'Access-Control-Allow-Origin' not in resp.headers:
        resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

class Resource(flask.ext.restful.Resource):

    representations = {'application/json': to_json}
    headers = ['content-type', 'authorization']

    def options(self, **kwargs):
        resp = app.make_default_options_response()

        h = resp.headers
        h['Access-Control-Allow-Origin'] = '*'
        h['Access-Control-Allow-Methods'] = resp.headers['Allow']
        h['Access-Control-Allow-Headers'] = ', '.join([x.upper() for x in self.headers])
        h['Access-Control-Max-Age'] = str(3600)

        return resp

class JSONEncoder(flask.json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)

        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%S%z')

        super(JSONEncoder, self).default(o)
