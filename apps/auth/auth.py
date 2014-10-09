import logging
from eve.auth import TokenAuth
from flask import current_app as app, request
import flask
from apps.auth.errors import AuthRequiredError, ForbiddenError
from superdesk.resource import Resource
from superdesk import get_resource_service


logger = logging.getLogger(__name__)


class AuthUsersResource(Resource):
    """ This resource is for authentication only.

    On users `find_one` never returns a password due to the projection.
    """
    datasource = {'source': 'users'}
    schema = {
        'username': {
            'type': 'string',
        },
        'password': {
            'type': 'string',
        },
        'status': {
            'type': 'string'
        }
    }
    item_methods = []
    resource_methods = []
    internal_resource = True


class AuthResource(Resource):
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
        'user': Resource.rel('users', True)
    }
    resource_methods = ['POST']
    item_methods = ['GET']
    public_methods = ['POST']
    extra_response_fields = ['user', 'token', 'username']


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

        # is the operation against the user record of the current user
        if request.view_args.get('_id') == str(user['_id']):
            # no user is allowed to delete their own user
            if method.lower() == 'delete':
                raise ForbiddenError
            else:
                return True

        # We allow all reads
        perm_method = self.method_map[method.lower()]
        if perm_method is 'read':
            return True

        # Read the user type
        user_type = user.get('user_type')

        # We allow all writes to administrators
        if user_type == 'administrator':
            return True

        # Only administrators can write to those resources in this list
        if resource in {'users', 'roles'}:
            raise ForbiddenError()

        # Get the list of roles belonging to this user
        roles = user.get('roles')
        if roles is not None:
            for role_id in roles:
                # check the permissions for each role
                while role_id:
                    role = get_resource_service('roles').find_one(_id=role_id, req=None) or {}
                    perm = role.get('permissions', {})
                    if perm.get(resource, {}).get(perm_method, False):
                        return True
                    role_id = role.get('extends')

        # If we didn't return True so far then user is not authorized
        raise ForbiddenError()

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid"""
        auth_token = get_resource_service('auth').find_one(token=token, req=None)
        if auth_token:
            user_id = str(auth_token['user'])
            flask.g.user = get_resource_service('users').find_one(req=None, _id=user_id)
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
