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

def create_user(userdata=None, db=None, **kwargs):
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

def format_user(user):
    user.pop('password', None)
    user.setdefault('_links', {
        'self': {'href': url_for('user', username=user.get('username'))}
    })
    return user

def find_one(username, db=None):
    return db.users.find_one({'username': username})

def find_users(db=None):
    return db.users.find()

def remove_user(username, db=None):
    return db.users.remove({'username': username})

def patch_user(user, data, db=None):
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

def on_create_users(db, docs):
    for doc in docs:
        now = datetime.utcnow()
        doc.setdefault('created', now)
        doc.setdefault('updated', now)

class CreateUserCommand(superdesk.Command):

    option_list = (
        superdesk.Option('--username', '-u', dest='username'),
        superdesk.Option('--password', '-p', dest='password'),
    )

    def run(self, username, password):
        if username and password:
            user = {
                'username': username,
                'password': password,
            }

            superdesk.app.data.insert('users', [user])
            return user

superdesk.connect('create:users', on_create_users)

superdesk.command('users:create', CreateUserCommand())

superdesk.domain('users', {
    'additional_lookup': {
        'url': '[\w]+',
        'field': 'username'
    },
    'schema': {
        'username': {
            'type': 'string',
            'unique': True,
        },
        'password': {
            'type': 'string',
        },
        'first_name': {
            'type': 'string',
        },
        'last_name': {
            'type': 'string',
        },
        'display_name': {
            'type': 'string',
        },
        'user_info': {
            'type': 'dict'
        }
    },
    'datasource': {
        'projection': {
            'username': 1,
            'first_name': 1,
            'last_name': 1,
            'display_name': 1,
            'user_info': 1,
        }
    }
})
