
import os
import unittest

from .parser import ANSAParser
from superdesk.etree import etree


class ANSAParserTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = ANSAParser()
        with open(os.path.join(os.path.dirname(__file__), 'item.xml')) as f:
            self.xml = etree.fromstring(f.read().encode('utf-8'))

    def test_parse_item(self):
        item = self.parser.parse(self.xml)[0]
        self.assertEqual('De Magistris, rafforzamento forze ordine e strutture dello Stato', item.get('abstract'))
        self.assertGreater(item['word_count'], 0)
        self.assertEqual([{'qcode': 'chronicle', 'name': 'Chronicle'}], item.get('anpa_category'))
