import os
from .ldap import authenticate
from superdesk.tests import TestCase
from .commands import ImportUserProfileFromADCommand


class ImportUsersTestCase(TestCase):

    def test_create_user_command(self):
        if 'LDAP_SERVER' in os.environ:
            user = {'username': 'superdesk', 'password': 'superdesk', 'user_to_import': 'superdesk'}
            cmd = ImportUserProfileFromADCommand()
            with self.app.test_request_context():
                cmd.run(user['username'], user['password'], user['user_to_import'])
                auth_user = authenticate(user, self.app)
                self.assertEquals(auth_user['username'], user['username'])

                cmd.run(user['username'], user['password'], user['user_to_import'])
                auth_user2 = authenticate(user, self.app)
                self.assertEquals(auth_user2['username'], user['username'])

                self.assertEquals(auth_user2['_id'], auth_user['_id'])
