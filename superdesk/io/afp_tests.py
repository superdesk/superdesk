import os
import unittest
from superdesk.io.newsml_1_2 import Parser
from superdesk.etree import etree
import datetime


class TestCase(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', 'afp.xml')
        with open(fixture) as f:
            self.item = Parser().parse_message(etree.fromstring(f.read()))

    def test_headline(self):
        self.assertEquals(self.item.get('headline'), 'Sweden court accepts receivership for Saab carmaker')

    def test_guid(self):
        self.assertEquals(self.item.get('guid'), 'urn:newsml:afp.com:20140829T135002Z:TX-PAR-FXW86:1')

    def test_coreitemvalues(self):
        self.assertEquals(self.item.get('provider'), 'AFP')
        self.assertEquals(self.item.get('type'), 'text')
        self.assertEquals(self.item.get('urgency'), '4')
        self.assertEquals(self.item.get('version'), '1')
        self.assertEquals(self.item.get('versioncreated'), datetime.datetime(2014, 8, 29, 13, 49, 51))
        self.assertEquals(self.item.get('firstcreated'), datetime.datetime(2014, 8, 29, 13, 49, 51))
        self.assertEquals(self.item.get('pubstatus'), 'Usable')

    def test_subjects(self):
        self.assertEquals(len(self.item.get('subject')), 8)
        self.assertIn({'cat': 'ECO', 'FormalName': '04011002'}, self.item.get('subject'))
        self.assertIn({'cat': 'ECO', 'FormalName': '04016007'}, self.item.get('subject'))
        self.assertIn({'cat': 'ECO', 'FormalName': '04000000'}, self.item.get('subject'))
        self.assertIn({'cat': 'ECO', 'FormalName': '04016038'}, self.item.get('subject'))
        self.assertIn({'cat': 'ECO', 'FormalName': '04011000'}, self.item.get('subject'))

if __name__ == '__main__':
    unittest.main()
