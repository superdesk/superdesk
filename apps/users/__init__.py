# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

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

    # Registering with intrinsic privileges because: A user should be allowed to update their own profile.
    superdesk.intrinsic_privilege(resource_name='users', method=['PATCH'])
