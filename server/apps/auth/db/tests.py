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
from test_factory import SuperdeskTestCase
from superdesk import get_resource_service
from .commands import CreateUserCommand


class UsersTestCase(SuperdeskTestCase):

    def test_create_user_command(self):
        if not LDAP_SERVER:
            user = {'username': 'foo', 'password': 'bar', 'email': 'baz'}
            cmd = CreateUserCommand()
            cmd.run(user['username'], user['password'], user['email'], admin='true')
            auth_user = get_resource_service('auth').authenticate(user)
            self.assertEquals(auth_user['username'], user['username'])

            cmd.run(user['username'], user['password'], user['email'], admin='true')
            auth_user2 = get_resource_service('auth').authenticate(user)
            self.assertEquals(auth_user2['username'], user['username'])
            self.assertEquals(auth_user2['_id'], auth_user['_id'])
