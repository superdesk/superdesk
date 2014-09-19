import superdesk
from superdesk.tests import TestCase
from .users import CreateUserCommand
from apps.auth import authenticate


class UsersTestCase(TestCase):

    def test_create_user_command(self):
        if not superdesk.is_ldap:
            user = {'username': 'foo', 'password': 'bar', 'email': 'baz'}
            cmd = CreateUserCommand()
            with self.app.test_request_context():
                cmd.run(user['username'], user['password'], user['email'])
                auth_user = authenticate(user, self.app.data)
                self.assertEquals(auth_user['username'], user['username'])

                cmd.run(user['username'], user['password'], user['email'])
                auth_user2 = authenticate(user, self.app.data)
                self.assertEquals(auth_user2['username'], user['username'])
                self.assertEquals(auth_user2['_id'], auth_user['_id'])
        else:
            pass
        #TODO: python3-ldap framework doesn't have test module to mock AD. Figure out a way to mock AD...