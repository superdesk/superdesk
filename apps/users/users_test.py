
import superdesk
from superdesk.tests import TestCase
from .services import UsersService


class PrivilegesTestCase(TestCase):

    def test_admin_has_all_privileges(self):
        with self.app.app_context():
            service = UsersService('users', backend=superdesk.get_backend())
            user = {'user_type': 'administrator'}
            service.set_privileges(user)
            self.assertEqual(user['active_privileges']['users'], 1)
