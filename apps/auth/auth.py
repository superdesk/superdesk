import logging
from eve.auth import TokenAuth
from flask import current_app as app, request
import flask
from apps.auth.errors import AuthRequiredError, ForbiddenError
from superdesk.resource import Resource
from superdesk import get_resource_service, get_resource_privileges


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
        'is_active': {
            'type': 'boolean'
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
    item_methods = ['GET', 'DELETE']
    public_methods = ['POST']
    extra_response_fields = ['user', 'token', 'username']


class SuperdeskTokenAuth(TokenAuth):
    """Superdesk Token Auth"""

    def check_permissions(self, resource, method, user):
        if not user:
            return True

        # is the operation against the user record of the current user
        if request.view_args.get('_id') == str(user['_id']):
            # no user is allowed to delete their own user
            if method.lower() in('delete', 'put'):
                raise ForbiddenError
            else:
                return True

        # We allow all reads or if resource is prepopulate then allow all
        if method == 'GET' or resource == 'prepopulate':
            return True

        # users should be able to change only their preferences
        if resource == 'preferences':
            session = get_resource_service('preferences').find_one(_id=request.view_args.get('_id'), req=None)
            return user['_id'] == session.get("user")

        # Get the list of privileges belonging to this user
        get_resource_service('users').set_privileges(user, flask.g.role)
        privileges = user.get('active_privileges', {})
        resource_privileges = get_resource_privileges(resource).get(method, None)
        if privileges.get(resource_privileges, False):
            return True

        # If we didn't return True so far then user is not authorized
        raise ForbiddenError()

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid"""
        auth_token = get_resource_service('auth').find_one(token=token, req=None)
        if auth_token:
            user_id = str(auth_token['user'])
            flask.g.user = get_resource_service('users').find_one(req=None, _id=user_id)
            flask.g.role = get_resource_service('users').get_role(flask.g.user)
            flask.g.auth = auth_token
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
