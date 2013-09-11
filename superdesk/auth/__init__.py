from functools import wraps
from base64 import b64decode

from flask import request, make_response
from flask.ext import restful

from superdesk import api, mongo, utils
from superdesk.rest import Resource

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if get_auth_token():
            return f(*args, **kwargs)
        restful.abort(401)
    return wrapper

def create_token(user):
    token_id = utils.get_random_string(40)
    token = {
        'token': token_id,
        'user': {
            'username': user.get('username')
        }
    }

    mongo.db.tokens.save(token)
    return token

def get_auth_token():
    """Get token data for token in Authorization header"""
    token = b64decode(request.headers.get('Authorization', '').replace('Basic ', ''))[:40]
    return mongo.db.tokens.find_one({'token': token.decode('ascii')})

def authenticate(**kwargs):
    if 'username' not in kwargs:
        raise AuthException("invalid credentials")

    user = mongo.db.users.find_one({'username': kwargs.get('username')})
    if not user:
        raise AuthException("username not found")

    if user.get('password') != kwargs.get('password'):
        raise AuthException("invalid credentials")

    return user

class AuthException(Exception):
    pass

class AuthResource(Resource):

    @auth_required
    def get(self):
        return get_auth_token()

    def post(self):
        try:
            user = authenticate(**request.get_json())
            token = create_token(user)
            return token, 201
        except AuthException as err:
            return {'message': err.args[0], 'code': 401}, 401

api.add_resource(AuthResource, '/auth')
