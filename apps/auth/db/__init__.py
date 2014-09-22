from apps.auth import AuthResource
import superdesk
from .db import DbAuthService, authenticate  # noqa


def init_app(app):
    endpoint_name = 'auth'
    service = DbAuthService(endpoint_name, backend=superdesk.get_backend())
    AuthResource(endpoint_name, app=app, service=service)
