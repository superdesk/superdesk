
import os
import flask
import unittest

from httmock import urlmatch, HTTMock

from .search import AnsaPictureProvider


@urlmatch(netloc=r'172.20.14.88')
def ansa_mock(url, request):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'ansafoto.json')) as f:
        return f.read()


class AnsaPictureTestCase(unittest.TestCase):

    def setUp(self):
        self.service = AnsaPictureProvider({})
        self.app = flask.Flask(__name__)
        self.app.config['ANSA_PHOTO_API'] = 'http://172.20.14.88/'

    def test_find(self):
        with HTTMock(ansa_mock):
            with self.app.app_context():
                items = self.service.find({})
        self.assertEqual(1, len(items))
        item = items[0]
        self.assertIn('headline', item)
        self.assertIn('type', item)
        self.assertIn('versioncreated', item)
        self.assertIn('description_text', item)
        self.assertIn('renditions', item)
