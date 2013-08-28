from functools import wraps
from base64 import b64decode

from flask import request
from flask.ext import restful

from superdesk import redis, auth

def is_authenticated(request):
    token = b64decode(request.headers.get('Authorization', '').replace('Basic ', ''))[:40]
    return auth.check_token(token)

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if is_authenticated(request):
            return f(*args, **kwargs)
        restful.abort(401)
    return wrapper
