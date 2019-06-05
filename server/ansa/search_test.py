
import os
import flask
import unittest

from httmock import urlmatch, HTTMock

from .search import AnsaPictureProvider, set_default_search_operator


@urlmatch(netloc=r'172.20.14.88')
def ansa_mock(url, request):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'ansafoto.json')) as f:
        return f.read()


class AnsaPictureTestCase(unittest.TestCase):

    def setUp(self):
        self.service = AnsaPictureProvider({'config': {'username': 'foo', 'password': 'bar'}})
        self.app = flask.Flask(__name__)
        self.app.config['ANSA_PHOTO_API'] = 'http://172.20.14.88/'

    def test_find(self):
        with HTTMock(ansa_mock):
            with self.app.app_context():
                items = self.service.find({})
                self.assertEqual(0, len(items))  # no query, no api call

                items = self.service.find({'query': {'filtered': {'query': {'query_string': {'query': 'foo'}}}}})
        self.assertEqual(1, len(items))
        item = items[0]
        self.assertIn('headline', item)
        self.assertIn('type', item)
        self.assertIn('versioncreated', item)
        self.assertIn('description_text', item)
        self.assertIn('renditions', item)

    def test_default_search_operator(self):
        params = {'searchtext': 'foo bar'}
        set_default_search_operator(params)
        self.assertEqual('foo AND bar', params['searchtext'])

        params['searchtext'] = '"foo bar"'
        set_default_search_operator(params)
        self.assertEqual('"foo bar"', params['searchtext'])

        params['searchtext'] = 'foo OR bar'
        set_default_search_operator(params)
        self.assertEqual('foo OR bar', params['searchtext'])

        params['searchtext'] = 'foo "juventus turin" bar'
        set_default_search_operator(params)
        self.assertEqual('foo AND "juventus turin" AND bar', params['searchtext'])
