import bcrypt
from flask import current_app as app
from apps.auth.errors import NotFoundAuthError, raiseCredentialsAuthError
from superdesk import utils as utils
from superdesk.services import BaseService


class DbAuthService(BaseService):
    def on_create(self, docs):
        for doc in docs:
            user = authenticate(doc, app)
            doc['user'] = user['_id']
            doc['token'] = utils.get_random_string(40)
            del doc['password']


def authenticate(credentials, app):
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
