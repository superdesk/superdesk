"""Superdesk Users"""

import bcrypt
from flask import current_app as app

import superdesk
from superdesk.base_model import BaseModel
from superdesk.utc import utcnow
from superdesk.activity import add_activity


class EmptyUsernameException(Exception):
    def __str__(self):
        return """Username is empty"""


class ConflictUsernameException(Exception):
    def __str__(self):
        return "Username '%s' exists already" % self.args[0]


def get_display_name(user):
    if user.get('first_name') or user.get('last_name'):
        display_name = '%s %s' % (user.get('first_name'), user.get('last_name'))
        return display_name.strip()
    else:
        return user.get('username')


def on_read_users(data, docs):
    """Set default fields for users"""
    for doc in docs:
        doc.setdefault('display_name', get_display_name(doc))
        if doc.get('password'):
            del doc['password']


def ensure_hashed_password(doc):
    if doc.get('password', None):
        doc['password'] = hash_password(doc.get('password'))


def hash_password(password):
    work_factor = app.config['BCRYPT_GENSALT_WORK_FACTOR']
    hashed = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt(work_factor))
    return hashed.decode('UTF-8')


class CreateUserCommand(superdesk.Command):
    """Create a user with given username, password and email.
    If user with given username exists, reset password.
    """

    option_list = (
        superdesk.Option('--username', '-u', dest='username', required=True),
        superdesk.Option('--password', '-p', dest='password', required=True),
        superdesk.Option('--email', '-e', dest='email', required=True),
    )

    def run(self, username, password, email):
        userdata = {
            'username': username,
            'password': password,
            'email': email,
        }

        user = superdesk.app.data.find_one('users', username=userdata.get('username'), req=None)
        if user:
            userdata[app.config['LAST_UPDATED']] = utcnow()
            userdata['password'] = hash_password(userdata['password'])
            superdesk.apps['users'].update(user.get('_id'), userdata, trigger_events=False)
            return userdata
        else:
            userdata[app.config['DATE_CREATED']] = utcnow()
            userdata[app.config['LAST_UPDATED']] = utcnow()
            superdesk.apps['users'].create([userdata], trigger_events=True)
            return userdata


class HashUserPasswordsCommand(superdesk.Command):
    def run(self):
        users = superdesk.app.data.find_all('auth_users')
        for user in users:
            pwd = user.get('password')
            if not pwd.startswith('$2a$'):
                updates = {}
                hashed = hash_password(user['password'])
                user_id = user.get('_id')
                updates['password'] = hashed
                superdesk.apps['users'].update(id=user_id, updates=updates, trigger_events=False)


superdesk.connect('read:users', on_read_users)
superdesk.connect('created:users', on_read_users)
superdesk.command('users:create', CreateUserCommand())
superdesk.command('users:hash_passwords', HashUserPasswordsCommand())


class UserRolesModel(BaseModel):

    endpoint_name = 'user_roles'
    schema = {
        'name': {
            'type': 'string',
            'unique': True,
            'required': True,
        },
        'extends': {
            'type': 'objectid'
        },
        'permissions': {
            'type': 'dict'
        }
    }
    datasource = {
        'default_sort': [('created', -1)]
    }


class UsersModel(BaseModel):
    endpoint_name = 'users'
    additional_lookup = {
        'url': 'regex("[\w]+")',
        'field': 'username'
    }
    schema = {
        'username': {
            'type': 'string',
            'unique': True,
            'required': True,
            'minlength': 1
        },
        'password': {
            'type': 'string',
            'minlength': 5
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
        'email': {
            'unique': True,
            'type': 'email',
            'required': True
        },
        'phone': {
            'type': 'phone_number',
        },
        'user_info': {
            'type': 'dict'
        },
        'picture_url': {
            'type': 'string',
        },
        'avatar': BaseModel.rel('upload', True),
        'role': BaseModel.rel('user_roles', True),
        'workspace': {
            'type': 'dict'
        }
    }

    extra_response_fields = [
        'display_name',
        'username',
        'email',
        'user_info',
        'picture_url',
        'avatar',
    ]

    datasource = {
        'projection': {
            'password': 0
        }
    }

    def on_create(self, docs):
        for doc in docs:
            ensure_hashed_password(doc)

    def on_created(self, docs):
        for doc in docs:
            add_activity('created user {{user}}', user=doc.get('display_name', doc.get('username')))

    def on_deleted(self, doc):
        add_activity('removed user {{user}}', user=doc.get('display_name', doc.get('username')))
