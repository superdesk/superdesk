from .reset_password import ResetPasswordModel, ActiveTokensModel  # NOQA
from .users import UserRolesModel, UsersModel


def init_app(app):
    UsersModel(app=app)
    UserRolesModel(app=app)
