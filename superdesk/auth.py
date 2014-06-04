
import flask
import logging
import superdesk
import superdesk.utils as utils
from flask import json, current_app as app, request
from eve.auth import TokenAuth


logger = logging.getLogger(__name__)


class AuthRequiredError(superdesk.SuperdeskError):
    """Auth required error."""
    status_code = 401
    payload = {'auth': 1}


class AuthError(superdesk.SuperdeskError):
    """Base Auth Error"""
    status_code = 400
    payload = {'credentials': 1}


class NotFoundAuthError(AuthError):
    """Username Not Found Auth Error"""
    pass


class CredentialsAuthError(AuthError):
    """Credentials Not Match Auth Exception"""
    pass


class SuperdeskTokenAuth(TokenAuth):

    """Superdesk Token Auth"""

    method_map = {
        'get': 'read',
        'put': 'write',
        'patch': 'write',
        'post': 'write',
        'delete': 'write',
    }

    def check_permissions(self, resource, method, user):
        if not user:
            return True

        if request.view_args.get('_id') == str(user['_id']):
            return True

        perm_method = self.method_map[method.lower()]
        role_id = user.get('role')
        while role_id:
            role = app.data.find_one('user_roles', _id=role_id) or {}
            perm = role.get('permissions', {})
            if perm.get(resource, {}).get(perm_method, False):
                return True
            role_id = role.get('extends')
        return not user.get('role')  # allow if there is no role

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid"""
        auth_token = app.data.find_one('auth', token=token)
        if auth_token:
            user_id = str(auth_token['user'])
            flask.g.user = app.data.find_one('users', _id=user_id)
            return self.check_permissions(resource, method, flask.g.user)

    def authorized(self, allowed_roles, resource, method):
        """Ignores auth on home endpoint."""
        if not resource:
            return True
        if app.debug and request.args.get('skip_auth'):
            return True
        return super(SuperdeskTokenAuth, self).authorized(allowed_roles, resource, method)

    def authenticate(self):
        """ Returns 401 response with CORS headers."""
        raise AuthRequiredError()


def authenticate(credentials, db):
    if 'username' not in credentials:
        raise NotFoundAuthError()

    user = db.find_one('auth_users', username=credentials.get('username'))
    if not user:
        raise NotFoundAuthError()

    if not credentials.get('password') or user.get('password') != credentials.get('password'):
        logger.warning("Login failure: %s" % json.dumps(credentials))
        raise CredentialsAuthError()

    return user


def on_create_auth(data, docs):
    for doc in docs:
        user = authenticate(doc, data)
        doc['user'] = user['_id']
        doc['token'] = utils.get_random_string(40)

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
