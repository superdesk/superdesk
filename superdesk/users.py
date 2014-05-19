"""Superdesk Users"""

import superdesk
import base64


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

    if not userdata.get('username'):
        raise EmptyUsernameException()

    conflict_user = db.users.find_one({'username': userdata.get('username')})
    if conflict_user:
        raise ConflictUsernameException(userdata.get('username'))

    db.users.insert(userdata)
    return userdata


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
        if doc.get('upload_id'):
            upload_id = doc.get('upload_id')
            upload = superdesk.app.data.find_one('upload', _id=upload_id)
            media_file = superdesk.app.media.get(upload.get('media'))
            media_content = base64.encodestring(media_file.read())
            picture_url = 'data:' + media_file.content_type + ';base64,' + media_content.decode('utf-8')
            doc['picture_url'] = picture_url
        if doc.get('password'):
            del doc['password']


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


superdesk.connect('read:users', on_read_users)
superdesk.connect('created:users', on_read_users)

superdesk.command('users:create', CreateUserCommand())

superdesk.domain('users', {
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'username'
    },
    'schema': {
        'username': {
            'type': 'string',
            'unique': True,
            'required': True,
            'minlength': 1
        },
        'password': {
            'type': 'string',
            'minlength': 6
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
        },
        'phone': {
            'type': 'phone_number',
        },
        'user_info': {
            'type': 'dict'
        },
        'picture_url': {
            'type': 'string'
        },
        'upload_id': {
            'type': 'string'
        },
        'role': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'user_roles',
                'field': '_id',
                'embeddable': True
            }
        }
    },
    'extra_response_fields': [
        'display_name',
        'username',
        'email',
        'user_info',
        'picture_url',
        'upload_id',
    ],
    'datasource': {
        'projection': {
            'username': 1,
            'first_name': 1,
            'last_name': 1,
            'display_name': 1,
            'email': 1,
            'user_info': 1,
            'picture_url': 1,
            'upload_id': 1,
            'role': 1,
            '_created': 1,
            '_updated': 1,
        }
    }
})
