from .reset_password import ResetPasswordModel, ResetPasswordService, ActiveTokensModel  # NOQA
from .users import RolesModel, UsersModel, CreateUserCommand, UsersService  # noqa
import superdesk
from superdesk.services import BaseService


def init_app(app):
    endpoint_name = 'users'
    service = UsersService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    UsersModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'roles'
    service = BaseService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    RolesModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'reset_user_password'
    service = ResetPasswordService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ResetPasswordModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'active_tokens'
    service = BaseService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ActiveTokensModel(endpoint_name=endpoint_name, app=app, service=service)
