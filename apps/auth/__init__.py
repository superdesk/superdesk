from apps.auth.auth import SuperdeskTokenAuth
from .auth import AuthUsersResource, AuthResource  # noqa
from .sessions import SesssionsResource
import superdesk
from superdesk.services import BaseService
from .db.reset_password import reset_schema  # noqa


def init_app(app):
    app.auth = SuperdeskTokenAuth()  # Overwrite the app default auth

    endpoint_name = 'auth_users'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    AuthUsersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'sessions'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    SesssionsResource(endpoint_name, app=app, service=service)
