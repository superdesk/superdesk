
from .tests import TestCase
from superdesk import privilege, PRIVILEGES


class PrivilegeTestCase(TestCase):

    def test_privilege_registration(self):
        privilege(name='ingest', label='Ingest')
        privilege(name='archive', label='Archive')
        self.assertIn('ingest', PRIVILEGES)
        self.assertIn('archive', PRIVILEGES)
