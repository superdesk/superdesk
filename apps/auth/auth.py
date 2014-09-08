
import flask
import logging
import superdesk
import superdesk.utils as utils
from flask import json, current_app as app, request
from eve.auth import TokenAuth
from superdesk.models import BaseModel
import bcrypt


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
            role = app.data.find_one('user_roles', _id=role_id, req=None) or {}
            perm = role.get('permissions', {})
            if perm.get(resource, {}).get(perm_method, False):
                return True
            role_id = role.get('extends')
        return not user.get('role')  # allow if there is no role

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid"""
        auth_token = app.data.find_one('auth', token=token, req=None)
        if auth_token:
            user_id = str(auth_token['user'])
            flask.g.user = app.data.find_one('users', req=None, _id=user_id)
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

    user = db.find_one('auth_users', req=None, username=credentials.get('username'))
    if not user:
        raise NotFoundAuthError()

    password = credentials.get('password').encode('UTF-8')
    hashed = user.get('password').encode('UTF-8')

    if not (password and hashed):
        raiseCredentialsAuthError(credentials)

    try:
        rehashed = bcrypt.hashpw(password, hashed)
        if hashed != rehashed:
            raiseCredentialsAuthError(credentials)
    except ValueError:
        raiseCredentialsAuthError(credentials)

    return user


def raiseCredentialsAuthError(credentials):
    logger.warning("Login failure: %s" % json.dumps(credentials))
    raise CredentialsAuthError()


class AuthUsersModel(BaseModel):
    """ This resource is for authentication only.

    On users `find_one` never returns a password due to the projection.
    """

    endpoint_name = 'auth_users'
    datasource = {'source': 'users'}
    schema = {
        'username': {
            'type': 'string',
        },
        'password': {
            'type': 'string',
        }
    }
    item_methods = []
    resource_methods = []
    internal_resource = True


class AuthModel(BaseModel):
    endpoint_name = 'auth'
    schema = {
        'username': {
            'type': 'string',
            'required': True
        },
        'password': {
            'type': 'string',
            'required': True
        },
        'token': {
            'type': 'string'
        },
        'user': BaseModel.rel('users', True)
    }
    resource_methods = ['POST']
    item_methods = ['GET']
    public_methods = ['POST']
    extra_response_fields = ['user', 'token', 'username']

    def on_create(self, docs):
        for doc in docs:
            user = authenticate(doc, app.data)
            doc['user'] = user['_id']
            doc['token'] = utils.get_random_string(40)
            del doc['password']
