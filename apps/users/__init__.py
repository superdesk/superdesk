import os
from .users import RolesResource, UsersResource, ADUsersService, DBUsersService  # noqa
import superdesk
from superdesk.services import BaseService


def init_app(app):
    endpoint_name = 'users'
    service = ADUsersService(endpoint_name, backend=superdesk.get_backend()) if 'LDAP_SERVER' in os.environ \
        else DBUsersService(endpoint_name, backend=superdesk.get_backend())
    UsersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'roles'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    RolesResource(endpoint_name, app=app, service=service)
