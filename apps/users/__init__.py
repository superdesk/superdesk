from .reset_password import ResetPasswordModel, ActiveTokensModel  # NOQA
from .users import RolesModel, UsersModel, CreateUserCommand  # noqa


def init_app(app):
    UsersModel(app=app)
    RolesModel(app=app)
    ResetPasswordModel(app=app)
    ActiveTokensModel(app=app)
