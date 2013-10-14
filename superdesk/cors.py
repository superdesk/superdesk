
from datetime import timedelta
from flask import make_response, request, current_app
from functools import wraps
import settings

def crossdomain(f):
    max_age = 21600
    methods = None
    headers = ', '.join(settings.X_HEADERS)

    def get_methods():
        if methods is not None:
            return methods
        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            resp = current_app.make_default_options_response()
        else:
            resp = make_response(f(*args, **kwargs))

        h = resp.headers
        h['Access-Control-Allow-Origin'] = settings.X_DOMAINS
        h['Access-Control-Allow-Methods'] = get_methods()
        h['Access-Control-Max-Age'] = str(max_age)
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers
        return resp
    return wrapper
