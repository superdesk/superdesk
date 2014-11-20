
from .tests import TestCase
from superdesk.privilege import privilege, get_privilege_list, _privileges


class PrivilegeTestCase(TestCase):

    def test_privilege_registration(self):
        _privileges.clear()

        privilege(name='ingest', label='Ingest')
        privilege(name='archive', label='Archive')

        self.assertIn('ingest', _privileges)
        self.assertIn('archive', _privileges)

        self.assertEqual(2, len(get_privilege_list()))
