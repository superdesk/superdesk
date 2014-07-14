from .reset_password import ResetPasswordModel, ActiveTokens
from .users import UserRolesModel, UsersModel


def init_app(app):
    UsersModel(app=app)
    UserRolesModel(app=app)
    ActiveTokens(app=app)
    ResetPasswordModel(app=app)
