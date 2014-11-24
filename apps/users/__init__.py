from settings import LDAP_SERVER
from .users import RolesResource, UsersResource
from .services import ADUsersService, DBUsersService, RolesService, is_admin  # noqa
import superdesk


def init_app(app):
    endpoint_name = 'users'
    if LDAP_SERVER:
        service = ADUsersService(endpoint_name, backend=superdesk.get_backend())
    else:
        service = DBUsersService(endpoint_name, backend=superdesk.get_backend())
    UsersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'roles'
    service = RolesService(endpoint_name, backend=superdesk.get_backend())
    RolesResource(endpoint_name, app=app, service=service)


superdesk.privilege(name='users', label='User Management', description='User can manage users.')
superdesk.privilege(name='roles', label='Roles Management', description='User can manage roles.')
