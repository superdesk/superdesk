import logging

import flask
from flask import json, current_app as app, request
from eve.auth import TokenAuth
import bcrypt
from ldap3 import Connection, Server, SEARCH_SCOPE_WHOLE_SUBTREE
from ldap3.core.exceptions import LDAPException

import superdesk
import superdesk.utils as utils
from superdesk.models import BaseModel
from superdesk.utc import utcnow


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
            role = app.data.find_one('roles', _id=role_id, req=None) or {}
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


class ADAuth:
    """
    Handles Authentication against Active Directory.
    """
    def __init__(self, host, port, base_filter, user_filter, profile_attributes, fqdn):
        """
        Initializes the AD Server
        :param host: ldap server. for example ldap://aap.com.au
        :param port: default port is 389
        :param base_filter:
        :param user_filter:
        :param profile_attributes:
        """
        self.ldap_server = Server(host, (port if port is not None else 389))

        self.fqdn = fqdn
        self.base_filter = base_filter
        self.user_filter = user_filter
        self.profile_attrs = profile_attributes

    def authenticate_and_fetch_profile(self, username, password, username_for_profile=None):
        """
        Authenticates a user with credentials username and password against AD. If authentication is successful then it
        fetches a profile of a user identified by username_for_profile and if found the profile is returned.
        :param username: LDAP username
        :param password: LDAP password
        :param username_for_profile: Username of the profile to be fetched
        :return: user profile base on the LDAP_USER_ATTRIBUTES
        """

        if username_for_profile is None:
            username_for_profile = username

        if self.fqdn is not None:
            username = username + "@" + self.fqdn

        try:
            ldap_conn = Connection(self.ldap_server, auto_bind=True, user=username, password=password)

            user_filter = self.user_filter.format(username_for_profile)
            logger.info('base filter:{} user filter:{}'.format(self.base_filter, user_filter))

            with ldap_conn:
                result = ldap_conn.search(self.base_filter, user_filter, SEARCH_SCOPE_WHOLE_SUBTREE,
                              attributes=list(self.profile_attrs.keys()))

                response = dict()

                if result:
                    user_profile = ldap_conn.response[0]['attributes']

                    for ad_profile_attr, sd_profile_attr in self.profile_attrs.items():
                        response[sd_profile_attr] = \
                            user_profile[ad_profile_attr] if user_profile.__contains__(ad_profile_attr) else ''

                        response[sd_profile_attr] = \
                            response[sd_profile_attr][0] if isinstance(response[sd_profile_attr], list) \
                                else response[sd_profile_attr]

                return response
        except LDAPException as e:
            logger.error("Exception occurred. Login failed for user {}".format(username), e)
            raise AuthError()


def authenticate(credentials, app):
    if 'username' not in credentials:
        raise NotFoundAuthError()

    if superdesk.is_ldap:
        return authenticate_via_ad(credentials, app)
    else:
        return authenticate_via_db(credentials, app)


def authenticate_via_db(credentials, app):
    user = app.data.find_one('auth_users', req=None, username=credentials.get('username'))
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


def authenticate_via_ad(credentials, app):
    """
    Authenticates the user against Active Directory
    :param credentials: an object having "username" and "password" attributes
    :param app: Eve App object
    :return: if success returns User object, otherwise throws Error
    """
    settings = app.settings
    ad_auth = ADAuth(settings['LDAP_SERVER'], settings['LDAP_SERVER_PORT'], settings['LDAP_BASE_FILTER'],
                     settings['LDAP_USER_FILTER'], settings['LDAP_USER_ATTRIBUTES'], settings['LDAP_FQDN'])

    username = credentials.get('username')
    password = credentials.get('password')

    user_data = ad_auth.authenticate_and_fetch_profile(username, password)
    if len(user_data) == 0:
        raise NotFoundAuthError()

    db = app.data
    user = db.find_one('auth_users', req=None, username=username)

    if not user:
        user_data[app.config['DATE_CREATED']] = utcnow()
        user_data[app.config['LAST_UPDATED']] = utcnow()
        user_data['username'] = username
        db.insert('users', user_data)
        user = db.find_one('auth_users', req=None, username=username)

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
            user = authenticate(doc, app)
            doc['user'] = user['_id']
            doc['token'] = utils.get_random_string(40)
            del doc['password']
