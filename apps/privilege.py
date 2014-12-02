
import superdesk
from superdesk.utils import ListCursor
from superdesk.privilege import get_privilege_list


class PrivilegeService(superdesk.Service):

    def get(self, req, lookup):
        """Return all registered privileges."""
        return ListCursor(get_privilege_list())


class PrivilegeResource(superdesk.Resource):
    """Read-only resource with all privileges."""
    resource_methods = ['GET']
    item_methods = []


def init_app(app):
    PrivilegeResource('privileges', app=app, service=PrivilegeService())
