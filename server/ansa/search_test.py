
import os
import flask
import unittest
import superdesk

from unittest.mock import patch, create_autospec
from httmock import urlmatch, HTTMock
from ansa.constants import PHOTO_CATEGORIES_ID, PRODUCTS_ID

from apps.archive import ArchiveService
from .search import AnsaPictureProvider, set_default_search_operator


@urlmatch(netloc=r'172.20.14.88')
def ansa_mock(url, request):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'ansafoto.json')) as f:
        return f.read()


class Resource:
    def __init__(self, service):
        self.service = service


resources = {
    'archive': Resource(create_autospec(ArchiveService)),
}


class VocabulariesMock():
    def find_one(self, req, _id):
        if _id == PHOTO_CATEGORIES_ID:
            return {
                'items': [
                    {'name': 'foo', 'qcode': '123'},
                    {'name': 'SOI', 'qcode': '140'},
                ],
            }
        if _id == PRODUCTS_ID:
            return {
                'items': [
                    {'name': 'Sports', 'qcode': '0050000100004'},
                    {'name': 'Test', 'qcode': '0050000100005'},
                ],
            }

        raise ValueError(_id)


class AnsaPictureTestCase(unittest.TestCase):

    def setUp(self):
        self.service = AnsaPictureProvider({'config': {'username': 'foo', 'password': 'bar'}})
        self.app = flask.Flask(__name__)
        self.app.config['ANSA_PHOTO_API'] = 'http://172.20.14.88/'

    @patch.dict(superdesk.resources, resources)
    def test_find(self):
        with HTTMock(ansa_mock):
            with self.app.app_context():
                items = self.service.find({})
                self.assertEqual(0, len(items))  # no query, no api call

                items = self.service.find({'query': {'filtered': {'query': {'query_string': {'query': 'foo'}}}}})
        self.assertEqual(1, len(items))
        self.assertEqual(6732873, items.count())
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

    @patch('superdesk.get_resource_service')
    @patch('ansa.search.update_renditions')
    def test_fetch(self, update_renditions_mock, get_service_mock):
        get_service_mock.return_value = VocabulariesMock()
        with HTTMock(ansa_mock):
            with self.app.app_context():
                item = self.service.fetch('foo')
                self.assertIsNotNone(item)

        self.assertEqual('en', item['language'])
        self.assertEqual('FAROOQ KHAN / STRR', item['byline'])
        self.assertEqual('usage terms', item['usageterms'])
        self.assertEqual('copyright', item['copyrightholder'])
        self.assertEqual('copyright notice', item['copyrightnotice'])
        self.assertEqual('FAMILY', item['slugline'])
        self.assertEqual('STRR', item['sign_off'])

        self.assertEqual('ANSA', item['extra']['supplier'])
        self.assertEqual('SRINAGAR', item['extra']['city'])
        self.assertEqual('INDIA', item['extra']['nation'])
        self.assertEqual('STR', item['extra']['coauthor'])
        self.assertNotIn('DateRelease', item['extra'])
        self.assertNotIn('DateCreated', item['extra'])

        self.assertIn({
            'name': 'SOI',
            'qcode': '140',
            'scheme': PHOTO_CATEGORIES_ID,
        }, item['subject'])

        self.assertIn({
            'name': 'Sports',
            'qcode': '0050000100004',
            'scheme': PRODUCTS_ID,
        }, item['subject'])
