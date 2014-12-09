from superdesk import get_backend
from .resource import PackageResource, PackageVersionsResource
from .service import PackageService, PackagesVersionsService


def init_app(app):
    endpoint_name = 'packages'
    service = PackageService(endpoint_name, backend=get_backend())
    PackageResource(endpoint_name, app=app, service=service)

    endpoint_name = 'packages_versions'
    service = PackagesVersionsService(endpoint_name, backend=get_backend())
    PackageVersionsResource(endpoint_name, app=app, service=service)
