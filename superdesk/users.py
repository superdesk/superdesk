"""Superdesk Users"""

import superdesk
from .utc import utcnow

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
    userdata.setdefault('created', utcnow())
    userdata.setdefault('updated', userdata.get('created'))

    if not userdata.get('username'):
        raise EmptyUsernameException()

    conflict_user = db.users.find_one({'username': userdata.get('username')})
    if conflict_user:
        raise ConflictUsernameException(userdata.get('username'))

    db.users.insert(userdata)
    return userdata

def get_display_name(user):
    if user.get('display_name'):
        return user.get('display_name')

    if user.get('first_name') or user.get('last_name'):
        display_name = '%s %s' % (user.get('first_name'), user.get('last_name'))
        return display_name.strip()
    else:
        return user.get('username')

def on_create_users(data, docs):
    """Set default fields for users"""
    for doc in docs:
        now = utcnow()
        doc.setdefault('created', now)
        doc.setdefault('updated', now)
        doc.setdefault('display_name', get_display_name(doc))

class CreateUserCommand(superdesk.Command):
    """Create a user with given username and password.
    If user with given username exists, reset password.
    """

    option_list = (
        superdesk.Option('--username', '-u', dest='username'),
        superdesk.Option('--password', '-p', dest='password'),
    )

    def run(self, username, password):
        if username and password:
            userdata = {
                'username': username,
                'password': password,
            }

            user = superdesk.app.data.find_one('users', username=userdata.get('username'))
            if user:
                superdesk.app.data.update('users', user.get('_id'), userdata)
                return user
            else:
                superdesk.app.data.insert('users', [userdata])
                return userdata

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
            'required': True
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
        'email': {
            'type': 'string',
        },
        'user_info': {
            'type': 'dict'
        },
        'picture_url': {
            'type': 'string'
        }
    },
    'extra_response_fields': ['username', 'first_name', 'last_name', 'display_name', 'email', 'user_info', 'picture_url'],
    'datasource': {
        'projection': {
            'username': 1,
            'first_name': 1,
            'last_name': 1,
            'display_name': 1,
            'email': 1,
            'user_info': 1,
            'picture_url': 1
        }
    }
})
