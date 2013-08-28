
from flask import request

from superdesk.decorators import crossdomain
from superdesk.api import Resource
from superdesk import mongo, redis, utils

class AuthException(Exception):
    pass

class AuthResource(Resource):
    def post(self):
        try:
            user = authenticate(**request.get_json())
            token = get_token(user)
            return token, 201
        except AuthException as err:
            return {'message': err.args[0], 'code': 401}, 401

def get_token(user):
    user.pop('password', None)
    auth_token = {'user': user, 'token': utils.get_random_string(40)}
    redis.set(auth_token['token'], auth_token)
    return auth_token

def check_token(token):
    return redis.get(token)

def authenticate(**kwargs):
    if 'username' not in kwargs:
        raise AuthException("invalid credentials")

    user = mongo.db.users.find_one({'username': kwargs.get('username')})
    if not user:
        raise AuthException("username not found")

    if user.get('password') != kwargs.get('password'):
        raise AuthException("invalid credentials")

    return user
