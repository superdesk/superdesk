
from flask import request

from superdesk.decorators import crossdomain
from superdesk.api import Resource
from superdesk import utils

from superdesk import mongo

class AuthException(Exception):
    pass

class AuthResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                raise AuthException(400, "invalid credentials")

            user = mongo.db.users.find_one({'username': data.get('username')})
            if not user:
                raise AuthException(400, "username not found")

            if user.get('password') != data.get('password'):
                raise AuthException(400, "invalid credentials")

            user.pop('password', None)
            auth_token = {'user': user, 'token': utils.get_random_string(40)}
            mongo.db.auth_tokens.insert(auth_token)

            return auth_token, 201
        except AuthException as err:
            return {'message': err.args[1], 'code': err.args[0]}, err.args[0]
