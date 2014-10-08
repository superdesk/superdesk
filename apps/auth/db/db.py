import bcrypt
from apps.auth.errors import NotFoundAuthError, raiseCredentialsAuthError, UserInactiveError
from superdesk import utils as utils, get_resource_service
from superdesk.services import BaseService


class DbAuthService(BaseService):
    def on_create(self, docs):
        for doc in docs:
            user = authenticate(doc)
            doc['user'] = user['_id']
            doc['token'] = utils.get_random_string(40)
            del doc['password']


def authenticate(credentials):
    user = get_resource_service('auth_users').find_one(req=None, username=credentials.get('username'))
    if not user:
        raise NotFoundAuthError()

    if user.get('status', 'active') == 'inactive':
        raise UserInactiveError()

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
