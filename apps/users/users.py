"""Superdesk Users"""

import bcrypt
import logging
from flask import current_app as app
import superdesk
from superdesk.resource import Resource
from superdesk.utc import utcnow
from apps.activity import add_activity
from superdesk.services import BaseService


logger = logging.getLogger(__name__)


class EmptyUsernameException(Exception):
    def __str__(self):
        return """Username is empty"""


class ConflictUsernameException(Exception):
    def __str__(self):
        return "Username '%s' exists already" % self.args[0]


def is_hashed(pwd):
    """Check if given password is hashed."""
    return pwd.startswith('$2a$')


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
        doc.pop('password', None)


def ensure_hashed_password(doc):
    if doc.get('password', None) and not is_hashed(doc.get('password')):
        doc['password'] = hash_password(doc.get('password'))


def hash_password(password):
    work_factor = app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12)
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
            app.config['LAST_UPDATED']: utcnow(),
        }

        with app.test_request_context('/users', method='POST'):
            ensure_hashed_password(userdata)
            user = app.data.find_one('users', username=userdata.get('username'), req=None)
            if user:
                logger.info('updating user %s' % (userdata))
                app.data.update('users', user.get('_id'), userdata)
                return userdata
            else:
                logger.info('creating user %s' % (userdata))
                userdata[app.config['DATE_CREATED']] = userdata[app.config['LAST_UPDATED']]
                app.data.insert('users', [userdata])

            logger.info('user saved %s' % (userdata))
            return userdata


class HashUserPasswordsCommand(superdesk.Command):
    def run(self):
        users = superdesk.app.data.find_all('auth_users')
        for user in users:
            pwd = user.get('password')
            if not is_hashed(pwd):
                updates = {}
                hashed = hash_password(user['password'])
                user_id = user.get('_id')
                updates['password'] = hashed
                superdesk.app.data.update('users', user_id, updates=updates)


# class ImportUserProfileFromADCommand(superdesk.Command):
#     """
#     Responsible for importing a user profile from Active Directory (AD) to Mongo.
#     This command runs on assumption that the user executing this command and
#     the user whose profile need to be imported need not to be the same. Uses ad_username and ad_password to bind to AD
#     and then searches for a user identified by username_to_import and if found imports into Mongo.
#     """
#
#     option_list = (
#         superdesk.Option('--ad_username', '-adu', dest='ad_username', required=True),
#         superdesk.Option('--ad_password', '-adp', dest='ad_password', required=True),
#         superdesk.Option('--username_to_import', '-u', dest='username', required=True),
#     )
#
#     def run(self, ad_username, ad_password, username):
#         """
#         Imports or Updates a User Profile from AD to Mongo.
#         :param ad_username: Active Directory Username
#         :param ad_password: Password of Active Directory Username
#         :param username: Username as in Active Directory whose profile needs to be imported to Superdesk.
#         :return: User Profile.
#         """
#
#         if not superdesk.is_ldap:
#             raise InvalidCommand("Authentication using AD isn't enabled.
#                                  Consider using 'users:create' command instead")
#
#         # Authenticate and fetch profile from AD
#         settings = app.settings
#         ad_auth = ADAuth(settings['LDAP_SERVER'], settings['LDAP_SERVER_PORT'], settings['LDAP_BASE_FILTER'],
#                          settings['LDAP_USER_FILTER'], settings['LDAP_USER_ATTRIBUTES'], settings['LDAP_FQDN'])
#
#         user_data = ad_auth.authenticate_and_fetch_profile(ad_username, ad_password, username)
#
#         if len(user_data) == 0:
#             raise NotFoundAuthError()
#
#         # Check if User Profile already exists in Mongo
#         user = superdesk.app.data.find_one('users', username=username, req=None)
#
#         if user:
#             user_data[app.config['LAST_UPDATED']] = utcnow()
#             superdesk.apps['users'].update(user.get('_id'), user_data, trigger_events=False)
#             return user_data
#         else:
#             user_data[app.config['DATE_CREATED']] = utcnow()
#             user_data[app.config['LAST_UPDATED']] = utcnow()
#             user_data['username'] = username
#             superdesk.apps['users'].create([user_data], trigger_events=True)
#             return user_data
#

superdesk.connect('read:users', on_read_users)
superdesk.connect('created:users', on_read_users)
superdesk.command('users:create', CreateUserCommand())
superdesk.command('users:hash_passwords', HashUserPasswordsCommand())
# superdesk.command('users:copyfromad', ImportUserProfileFromADCommand())


class RolesResource(Resource):
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
        'default_sort': [('_created', -1)]
    }


class UsersResource(Resource):
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
        'avatar': Resource.rel('upload', True),
        'role': Resource.rel('roles', True),
        'preferences': {'type': 'dict'},
        'workspace': {
            'type': 'dict'
        },
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
            'password': 0,
            'preferences': 0
        }
    }


class UsersService(BaseService):

    def on_create(self, docs):
        for doc in docs:
            ensure_hashed_password(doc)

    def on_created(self, docs):
        for doc in docs:
            add_activity('created user {{user}}', user=doc.get('display_name', doc.get('username')))

    def on_deleted(self, doc):
        add_activity('removed user {{user}}', user=doc.get('display_name', doc.get('username')))
