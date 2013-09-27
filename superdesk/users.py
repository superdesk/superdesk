"""Superdesk Users"""

from flask import request, url_for
from datetime import datetime

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
    userdata.setdefault('created', datetime.utcnow())
    userdata.setdefault('updated', userdata.get('created'))

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
    user.setdefault('_links', {
        'self': {'href': url_for('user', username=user.get('username'))}
    })
    return user

def find_one(username, db=superdesk.db):
    return db.users.find_one({'username': username})

def find_users(db=superdesk.db):
    return db.users.find()

def remove_user(username, db=superdesk.db):
    return db.users.remove({'username': username})

def patch_user(user, data, db=superdesk.db):
    user.update(data)
    user.update({'updated': datetime.utcnow()})
    db.users.save(user)
    return user

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

class UserResource(Resource):

    def get(self, username):
        user = find_one(username=username)
        return format_user(user)

    def patch(self, username):
        user = find_one(username=username)
        patch_user(user, request.get_json())
        return format_user(user)

    def delete(self, username):
        return remove_user(username)

superdesk.api.add_resource(UserResource, '/users/<string:username>', endpoint='user')
superdesk.api.add_resource(UserListResource, '/users')
