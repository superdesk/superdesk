
import superdesk
from .dashboard import DashboardService, DashboardResource


def init_app(app):
    resource = 'dashboards'
    service = DashboardService(resource, backend=superdesk.get_backend())
    DashboardResource(resource, app=app, service=service)
    superdesk.intrinsic_privilege(resource, ['POST', 'PATCH'])
