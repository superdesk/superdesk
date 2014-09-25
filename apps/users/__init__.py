import os
from .users import RolesResource, UsersResource, ADUsersService, DBUsersService  # noqa
import superdesk
from superdesk.services import BaseService


def init_app(app):
    endpoint_name = 'users'
    if 'LDAP_SERVER' in os.environ:
        service = ADUsersService(endpoint_name, backend=superdesk.get_backend())
    else:
        service = DBUsersService(endpoint_name, backend=superdesk.get_backend())
    UsersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'roles'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    RolesResource(endpoint_name, app=app, service=service)
