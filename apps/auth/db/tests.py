from settings import LDAP_SERVER
from superdesk.tests import TestCase
from superdesk import get_resource_service
from .commands import CreateUserCommand


class UsersTestCase(TestCase):

    def test_create_user_command(self):
        if not LDAP_SERVER:
            user = {'username': 'foo', 'password': 'bar', 'email': 'baz'}
            cmd = CreateUserCommand()
            with self.app.test_request_context():
                cmd.run(user['username'], user['password'], user['email'])
                auth_user = get_resource_service('auth').authenticate(user)
                self.assertEquals(auth_user['username'], user['username'])

                cmd.run(user['username'], user['password'], user['email'])
                auth_user2 = get_resource_service('auth').authenticate(user)
                self.assertEquals(auth_user2['username'], user['username'])
                self.assertEquals(auth_user2['_id'], auth_user['_id'])
