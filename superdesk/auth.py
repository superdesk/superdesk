
import flask
import logging
import superdesk
import superdesk.utils as utils
from flask import json
from eve.auth import TokenAuth

logger = logging.getLogger(__name__)


class SuperdeskTokenAuth(TokenAuth):
    """Superdesk Token Auth"""

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid"""
        auth_token = flask.current_app.data.find_one('auth', token=token)
        if auth_token:
            user_id = str(auth_token['user'])
            flask.g.user = flask.current_app.data.find_one('users', _id=user_id)
        return auth_token


class AuthException(Exception):
    """Base Auth Exception"""
    pass


class NotFoundAuthException(AuthException):
    """Username Not Found Auth Exception"""
    pass


class CredentialsAuthException(AuthException):
    """Credentials Not Match Auth Exception"""
    pass


def authenticate(credentials, db):
    if 'username' not in credentials:
        raise NotFoundAuthException()

    user = db.find_one('auth_users', username=credentials.get('username'))
    if not user:
        raise NotFoundAuthException()

    if not credentials.get('password') or user.get('password') != credentials.get('password'):
        logger.warning("Login failure: %s" % json.dumps(credentials))
        raise CredentialsAuthException()

    return user


def on_create_auth(data, docs):
    for doc in docs:
        try:
            user = authenticate(doc, data)
            doc['user'] = user['_id']
            doc['token'] = utils.get_random_string(40)
        except NotFoundAuthException:
            superdesk.abort(404)
        except CredentialsAuthException:
            superdesk.abort(403)

superdesk.connect('create:auth', on_create_auth)

superdesk.domain('auth_users', {
    'datasource': {
        'source': 'users'
    },
    'schema': {
        'username': {
            'type': 'string',
        },
        'password': {
            'type': 'string',
        }
    },
    'item_methods': [],
    'resource_methods': []
})

superdesk.domain('auth', {
    'schema': {
        'username': {
            'type': 'string'
        },
        'password': {
            'type': 'string'
        },
        'token': {
            'type': 'string'
        },
        'user': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'users',
                'field': '_id',
                'embeddable': True
            }
        }
    },
    'resource_methods': ['POST'],
    'item_methods': ['GET'],
    'public_methods': ['POST'],
    'extra_response_fields': ['user', 'token', 'username']
})
