from apps.auth import AuthResource
from .reset_password import ResetPasswordService, ResetPasswordResource
import superdesk
from .db import DbAuthService, authenticate  # noqa
from .commands import CreateUserCommand, HashUserPasswordsCommand

def init_app(app):
    endpoint_name = 'auth'
    service = DbAuthService(endpoint_name, backend=superdesk.get_backend())
    AuthResource(endpoint_name, app=app, service=service)

    endpoint_name = 'reset_user_password'
    service = ResetPasswordService(endpoint_name, backend=superdesk.get_backend())
    ResetPasswordResource(endpoint_name, app=app, service=service)
