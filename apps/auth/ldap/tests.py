from settings import LDAP_SERVER
from superdesk.tests import TestCase
from superdesk import get_resource_service
from .commands import ImportUserProfileFromADCommand


class ImportUsersTestCase(TestCase):

    def test_create_user_command(self):
        if LDAP_SERVER:
            user = {'username': 'sduser1', 'password': 'Password.01', 'user_to_import': 'sduser1'}
            cmd = ImportUserProfileFromADCommand()
            with self.app.test_request_context():
                cmd.run(user['username'], user['password'], user['user_to_import'])
                auth_user = get_resource_service('auth').authenticate(user)
                self.assertEquals(auth_user['username'], user['username'])

                cmd.run(user['username'], user['password'], user['user_to_import'])
                auth_user2 = get_resource_service('auth').authenticate(user)
                self.assertEquals(auth_user2['username'], user['username'])

                self.assertEquals(auth_user2['_id'], auth_user['_id'])
