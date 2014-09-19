from .reset_password import ResetPasswordModel, ActiveTokensModel  # NOQA
import superdesk
from .users import RolesModel, UsersModel, CreateUserCommand  # noqa


def init_app(app):
    UsersModel(app=app)
    RolesModel(app=app)

    if not superdesk.isLDAP():
        ResetPasswordModel(app=app)

    ActiveTokensModel(app=app)
