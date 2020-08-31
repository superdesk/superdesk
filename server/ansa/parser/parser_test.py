
import os
import requests_mock

from pytz import timezone
from .parser import ANSAParser
from superdesk.etree import etree
from superdesk.tests import TestCase
from ansa.subjects import init_app as init_subjects

GEONAMES_URL = 'http://api.geonames.org/getJSON?type=json&username=superdesk_dev&geonameId=3172394&lang=it'


class ANSAParserTestCase(TestCase):

    def parse(self, fixture):
        parser = ANSAParser()
        with open(os.path.join(os.path.dirname(__file__), fixture)) as f:
            xml = etree.fromstring(f.read().encode('utf-8'))
            return parser.parse(xml)[0]

    def test_parse_item(self):
        init_subjects(self.app)
        item = self.parse('item.xml')
        self.assertEqual('De Magistris, rafforzamento forze ordine e strutture dello Stato', item['extra']['subtitle'])
        self.assertGreater(item['word_count'], 0)
        self.assertEqual([{'qcode': 'chronicle', 'name': 'Chronicle'}], item.get('anpa_category'))
        self.assertIn({'name': 'Product X', 'scheme': 'products', 'qcode': '123456789'}, item['subject'])
        self.assertEqual('tag:ansa.it,2017-02-24:ea58f9ce5951ece86fe126162c4fb161', item['guid'])
        self.assertEqual(item['guid'], item['extra']['ansaid'])
        self.assertEqual('2017-02-24T12:51:00+00:00', item['firstcreated'].isoformat())
        self.assertIn({'name': 'Giustizia, Criminalità', 'qcode': '02000000'}, item['subject'])

        extra = item.get('extra', {})
        self.assertEqual('Napoli', extra['city'])

    def test_parse_semantics(self):
        item = self.parse('semantics.xml')
        self.assertRegex(item['description_text'], r'ANSA/GIUSEPPE LAMI$')
        self.assertGreaterEqual(len(item['subject']), 3)
        self.assertIn({'name': 'Religious Leader', 'qcode': '12015000'}, item['subject'])
        self.assertIn({'name': 'REL', 'qcode': 'REL', 'scheme': 'PhotoCategories'}, item['subject'])
        self.assertIn('semantics', item)
        self.assertIn('iptcDomains', item['semantics'])
        self.assertIn('Religious Leader', item['semantics']['iptcDomains'])

    def test_parse_semantics_error(self):
        item = self.parse('semantics_wrong_json.xml')
        self.assertIsNotNone(item)

    def test_parse_image_rights(self):
        item = self.parse('semantics.xml')
        self.assertEqual('ANSA', item['creditline'])
        self.assertEqual('ANSA', item['copyrightholder'])
        self.assertIn('ANSA', item['copyrightnotice'])
        self.assertEqual('Not for use outside Italy', item['usageterms'])

    def test_populate_rights(self):
        self.app.data.insert('vocabularies', [{
            '_id': 'rightsinfo',
            'items': [
                {
                    'name': 'ansa',
                    'copyrightHolder': 'ANSA',
                    'copyrightNotice': 'ANSA notice',
                    'usageTerms': 'ANSA usage',
                },
            ]
        }])
        item = self.parse('semantics_missing_rights_info.xml')
        self.assertEqual('ANSA', item['copyrightholder'])
        self.assertEqual('ANSA notice', item['copyrightnotice'])
        self.assertEqual('ANSA usage', item['usageterms'])

    def test_located(self):
        with requests_mock.mock() as mock:
            with open(os.path.join(os.path.dirname(__file__), 'geonames.json'), mode='rb') as data:
                mock.get(GEONAMES_URL, content=data.read())
            item = self.parse('located.xml')
        dateline = item['dateline']
        located = dateline['located']
        self.assertEqual('Napoli', located['city'])
        self.assertIn('place', located)
        self.assertEqual('NAPOLI, 24 FEB', dateline['text'])
        self.assertIn('date', dateline)
        self.assertIn('tz', located)
        self.assertIsNotNone(timezone(located['tz']))

    def test_photo(self):
        item = self.parse('photo.xml')
        self.assertIn({'name': 'CLJ', 'qcode': 'CLJ', 'scheme': 'PhotoCategories'}, item['subject'])
        photo_subjects = [s for s in item['subject'] if s.get('qcode') == 'CLJ']
        self.assertEqual(1, len(photo_subjects))

        self.assertEqual('ADM', item.get('sign_off'))

        extra = item['extra']
        self.assertEqual('TANGERANG', extra['city'])
        self.assertEqual('Spain', extra['nation'])
        self.assertEqual('ANSA', extra['supplier'])
        self.assertEqual('sp/lrc', extra['Digitatore'])

    def test_culture(self):
        item = self.parse('culture.xml')

        self.assertIn('(ANSA) - ROMA, 1 LUG - TEST FROM XAWES', item['body_html'])

        self.assertIn('keywords', item)
        self.assertIn('culture', item['keywords'])
        self.assertIn('arts', item['keywords'])
        self.assertIn('fashion', item['keywords'])
        self.assertEqual('VR-BAR', item['sign_off'])

    def test_image_association(self):
        item = self.parse('culture.xml')
        self.assertIn('featuremedia', item.get('associations'))
        self.assertEqual({
            'residRef': 'featured.jpg',
            'description_text': 'featured caption',
        }, item['associations']['featuremedia'])

        self.assertIn('photoGallery--1', item['associations'])
        self.assertIn('photoGallery--2', item['associations'])
