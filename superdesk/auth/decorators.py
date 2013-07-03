from functools import wraps
from flask import request
from flask.ext import restful
from superdesk.users import is_valid_token

def is_authenticated(request):
    token = request.headers.get('Authorization', 'token ').replace('token ', '')
    return is_valid_token(token)

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if is_authenticated(request):
            return f(*args, **kwargs)

        restful.abort(401)
    return wrapper
