from .reset_password import ResetPasswordModel, ActiveTokensModel  # NOQA
from .users import UserRolesModel, UsersModel, CreateUserCommand  # noqa


def init_app(app):
    UsersModel(app=app)
    UserRolesModel(app=app)
    ResetPasswordModel(app=app)
    ActiveTokensModel(app=app)
