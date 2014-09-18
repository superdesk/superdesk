from .auth import SuperdeskTokenAuth, AuthUsersResource, AuthResource, AuthService, authenticate  # noqa
from .sessions import SesssionsResource
import superdesk
from superdesk.services import BaseService


def init_app(app):
    app.auth = SuperdeskTokenAuth()  # Overwrite the app default auth

    endpoint_name = 'auth_users'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    AuthUsersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'auth'
    service = AuthService(endpoint_name, backend=superdesk.get_backend())
    AuthResource(endpoint_name, app=app, service=service)

    endpoint_name = 'sessions'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    SesssionsResource(endpoint_name, app=app, service=service)
