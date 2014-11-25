
import superdesk
from superdesk.tests import TestCase
from .services import UsersService


class PrivilegesTestCase(TestCase):

    def test_admin_has_all_privileges(self):
        with self.app.app_context():
            service = UsersService('users', backend=superdesk.get_backend())
            user = {'user_type': 'administrator'}
            service.set_privileges(user, None)
            self.assertEqual(user['active_privileges']['users'], 1)

    def test_user_has_merged_privileges(self):
        with self.app.app_context():
            service = UsersService('users', backend=superdesk.get_backend())
            user = {'user_type': 'user', 'privileges': {'users': 1}}
            role = {'privileges': {'archive': 1}}
            service.set_privileges(user, role)
            self.assertEqual(user['active_privileges']['users'], 1)
            self.assertEqual(user['active_privileges']['archive'], 1)