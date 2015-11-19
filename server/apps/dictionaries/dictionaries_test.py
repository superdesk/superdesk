
from test_factory import SuperdeskTestCase
from settings import URL_PREFIX
import superdesk
from eve.utils import ParsedRequest

from apps.dictionaries.service import words, DictionaryService


class WordsTestCase(SuperdeskTestCase):

    def setUp(self):
        super().setUp()
        self.req = ParsedRequest()
        with self.app.test_request_context(URL_PREFIX):
            self.dictionaries = [{'_id': '1', 'name': 'Eng', 'language_id': 'en'},
                                 {'_id': '2', 'name': 'Eng AUs', 'language_id': 'en-AU', 'is_active': 'true'},
                                 {'_id': '3', 'name': 'French', 'language_id': 'fr'}]
            self.app.data.insert('dictionaries', self.dictionaries)

    def test_words_parsing(self):
        self.assertEquals(['abc'], words('abc'))
        self.assertEquals(['3d', 'x5'], words('3d 123 x5'))

    def test_base_language(self):
        self.assertEqual(DictionaryService().get_base_language('en-AU'), 'en')
        self.assertIsNone(DictionaryService().get_base_language('en'))

    def test_get_dictionary(self):
        with self.app.app_context():
            dicts = superdesk.get_resource_service('dictionaries').get_dictionaries('en')
            self.assertEqual(len(dicts), 1)
            self.assertEqual(dicts[0]['language_id'], 'en')
            dicts = superdesk.get_resource_service('dictionaries').get_dictionaries('en-AU')
            self.assertEqual(len(dicts), 1)
            self.assertEqual(dicts[0]['language_id'], 'en-AU')
