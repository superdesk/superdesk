
from superdesk.tests import TestCase
from superdesk.users import CreateUserCommand
from superdesk.auth import authenticate


class UsersTestCase(TestCase):

    def test_create_user_command(self):
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
