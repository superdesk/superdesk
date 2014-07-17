from .auth import AuthUsersModel, AuthModel
from .sessions import SesssionsModel


def init_app(app):
    AuthUsersModel(app)
    AuthModel(app)
    SesssionsModel(app=app)
