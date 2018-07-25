
import os

from .parser import ANSAParser
from superdesk.etree import etree
from superdesk.tests import TestCase


class ANSAParserTestCase(TestCase):

    def parse(self, fixture):
        parser = ANSAParser()
        with open(os.path.join(os.path.dirname(__file__), fixture)) as f:
            xml = etree.fromstring(f.read().encode('utf-8'))
            return parser.parse(xml)[0]

    def test_parse_item(self):
        item = self.parse('item.xml')
        self.assertEqual('De Magistris, rafforzamento forze ordine e strutture dello Stato', item['extra']['subtitle'])
        self.assertGreater(item['word_count'], 0)
        self.assertEqual([{'qcode': 'chronicle', 'name': 'Chronicle'}], item.get('anpa_category'))
        self.assertIn({'name': 'Product X', 'scheme': 'products', 'qcode': '123456789'}, item['subject'])

    def test_parse_semantics(self):
        item = self.parse('semantics.xml')
        self.assertRegex(item['description_text'], r'ANSA/GIUSEPPE LAMI$')
        self.assertEqual(2, len(item['subject']))
        self.assertIn({'name': 'Religious Leader', 'qcode': '12015000'}, item['subject'])
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
