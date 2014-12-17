
from flask import request
from nose.tools import assert_raises
from superdesk.tests import TestCase
from .auth import SuperdeskTokenAuth
from superdesk.errors import SuperdeskApiError


class UserAuthTestCase(TestCase):
    """Test what user can change in his profile."""

    def setUp(self):
        super().setUp()
        self.auth = SuperdeskTokenAuth()
        self.user = {'_id': '5374ce0a3b80a15fd8072403'}
        self.role = {}

    def test_user_can_not_delete_himself(self):
        with assert_raises(SuperdeskApiError) as error_context:
            with self.app.test_request_context('/api/users'):
                request.view_args.setdefault('_id', self.user.get('_id'))
                self.auth.check_permissions('users', 'delete', self.user)
        ex = error_context.exception
        self.assertTrue(ex.status_code == 403)

    def test_user_can_not_change_his_role(self):
        with self.app.test_request_context('/api/users'):
            request.view_args.setdefault('_id', self.user.get('_id'))
            self.assertTrue(self.auth.check_permissions('users', 'patch', self.user))
