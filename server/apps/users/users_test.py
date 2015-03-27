# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import flask
import superdesk
from superdesk.tests import TestCase
from .services import UsersService


class PrivilegesTestCase(TestCase):

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.service = UsersService('users', backend=superdesk.get_backend())

    def test_admin_has_all_privileges(self):
        with self.app.app_context():
            user = {'user_type': 'administrator'}
            self.service.set_privileges(user, None)
            self.assertEqual(user['active_privileges']['users'], 1)

    def test_user_has_merged_privileges(self):
        with self.app.app_context():
            user = {'user_type': 'user', 'privileges': {'users': 1}}
            role = {'privileges': {'archive': 1}}
            self.service.set_privileges(user, role)
            self.assertEqual(user['active_privileges']['users'], 1)
            self.assertEqual(user['active_privileges']['archive'], 1)

    def test_user_with_privilege_can_change_his_role(self):
        with self.app.app_context():
            flask.g.user = {'user_type': 'administrator'}
            ids = self.service.create([{'name': 'user', 'user_type': 'administrator'}])
            doc_old = self.service.find_one(None, _id=ids[0])
            self.service.update(ids[0], {'role': '1'}, doc_old)
            self.assertIsNotNone(self.service.find_one(req=None, role='1'))
