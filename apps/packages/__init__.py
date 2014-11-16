from superdesk import get_backend
from .resource import PackageResource
from .service import PackageService


def init_app(app):
    endpoint_name = 'packages'
    service = PackageService(endpoint_name, backend=get_backend())
    PackageResource(endpoint_name, app=app, service=service)
