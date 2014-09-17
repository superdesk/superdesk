from .reset_password import ResetPasswordResource, ResetPasswordService, ActiveTokensResource  # NOQA
from .users import RolesResource, UsersResource, CreateUserCommand, UsersService  # noqa
import superdesk
from superdesk.services import BaseService


def init_app(app):
    endpoint_name = 'users'
    service = UsersService(endpoint_name, backend=superdesk.get_backend())
    UsersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'roles'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    RolesResource(endpoint_name, app=app, service=service)

    endpoint_name = 'reset_user_password'
    service = ResetPasswordService(endpoint_name, backend=superdesk.get_backend())
    ResetPasswordResource(endpoint_name, app=app, service=service)

    endpoint_name = 'active_tokens'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    ActiveTokensResource(endpoint_name, app=app, service=service)
