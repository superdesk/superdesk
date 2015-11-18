
import flask
import unittest
import unittest.mock
from . import push_content_notification


class PushContentNotificationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    @unittest.mock.patch('apps.content.push_notification')
    def test_push_content_notification(self, push_notification):
        foo1 = {'_id': 'foo', 'task': {'desk': 'sports', 'stage': 'inbox'}}
        foo2 = {'_id': 'foo', 'task': {'desk': 'news', 'stage': 'todo'}}
        foo3 = {'_id': 'foo'}

        push_content_notification([foo1, foo2, foo3])
        push_notification.assert_called_once_with(
            'content:update',
            user='',
            items={'foo': 1},
            desks={'sports': 1, 'news': 1},
            stages={'inbox': 1, 'todo': 1}
        )
