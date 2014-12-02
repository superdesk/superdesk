
import flask
import superdesk
from nose.tools import raises
from superdesk.tests import TestCase
from .services import UsersService
from apps.auth.errors import ForbiddenError


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

    @raises(ForbiddenError)
    def test_user_can_not_change_his_role(self):
        with self.app.app_context():
            flask.g.user = {'user_type': 'user'}
            ids = self.service.create([{'name': 'user'}])
            self.service.update(ids[0], {'role': '1'})

    def test_user_with_privilege_can_change_his_role(self):
        with self.app.app_context():
            flask.g.user = {'user_type': 'administrator'}
            ids = self.service.create([{'name': 'user', 'user_type': 'administrator'}])
            self.service.update(ids[0], {'role': '1'})
            self.assertIsNotNone(self.service.find_one(req=None, role='1'))
