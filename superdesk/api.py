"""Base API Resource

Idea is to extend those and not depend on the other library.

Currently it provides CORS.
"""

from flask import current_app
from flask.ext import restful

HEADERS = ['content-type', 'authorization']

class Resource(restful.Resource):

    def options(self, **kwargs):
        resp = current_app.make_default_options_response()

        h = resp.headers
        h['Access-Control-Allow-Origin'] = '*'
        h['Access-Control-Allow-Methods'] = resp.headers['Allow']
        h['Access-Control-Allow-Headers'] = ', '.join([x.upper() for x in HEADERS])
        h['Access-Control-Max-Age'] = str(3600)

        return resp
