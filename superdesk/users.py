"""Superdesk Users"""

from flask import request

import superdesk
from .api import Resource

class EmptyUsernameException(Exception):
    def __str__(self):
        return """Username is empty"""

class ConflictUsernameException(Exception):
    def __str__(self):
        return "Username '%s' exists already" % self.args[0]

@superdesk.manager.option('--username', '-u', dest='username')
@superdesk.manager.option('--password', '-p', dest='password')
def create_user(userdata=None, db=superdesk.db, **kwargs):
    """Create a new user"""

    if not userdata:
        userdata = {}

    userdata.update(kwargs)

    if not userdata.get('username'):
        raise EmptyUsernameException()

    conflict_user = db.users.find_one({'username': userdata.get('username')})
    if conflict_user:
        raise ConflictUsernameException(userdata.get('username'))

    db.users.insert(userdata)
    return userdata

def drop_users(db=superdesk.db):
    db.users.remove()

def format_user(user):
    user.pop('password', None)
    return user

def find_users(db=superdesk.db):
    return db.users.find()

def get_token(user):
    token = AuthToken(token=utils.get_random_string(40), user=user)
    token.save()
    return token

def is_valid_token(auth_token):
    try:
        token = AuthToken.objects.get(token=auth_token)
        return token.is_valid()
    except AuthToken.DoesNotExist:
        return False

class UserListResource(Resource):

    def get(self):
        users = [format_user(user) for user in find_users()]
        return {'data': users, '_list': {'total_count': len(users)}}

    def post(self):
        user = create_user(request.get_json())
        return format_user(user), 201

superdesk.api.add_resource(UserListResource, '/users')
