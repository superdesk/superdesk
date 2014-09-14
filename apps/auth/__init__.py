from .auth import SuperdeskTokenAuth, AuthUsersModel, AuthModel, AuthService, authenticate  # noqa
from .sessions import SesssionsModel
import superdesk
from superdesk.services import BaseService


def init_app(app):
    app.auth = SuperdeskTokenAuth()  # Overwrite the app default auth

    endpoint_name = 'auth_users'
    service = BaseService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    AuthUsersModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'auth'
    service = AuthService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    AuthModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'sessions'
    service = BaseService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    SesssionsModel(endpoint_name=endpoint_name, app=app, service=service)
