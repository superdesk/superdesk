from .auth import SuperdeskTokenAuth, AuthUsersModel, AuthModel, authenticate  # noqa
from .sessions import SesssionsModel


def init_app(app):
    app.auth = SuperdeskTokenAuth()
    AuthUsersModel(app)
    AuthModel(app)
    SesssionsModel(app=app)
