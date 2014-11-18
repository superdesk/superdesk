import os
import unittest
from superdesk.io.newsml_1_2 import NewsMLOneParser
from superdesk.etree import etree
import datetime


class TestCase(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', 'afp.xml')
        with open(fixture) as f:
            self.item = NewsMLOneParser().parse_message(etree.fromstring(f.read()))

    def test_headline(self):
        self.assertEquals(self.item.get('headline'), 'Sweden court accepts receivership for Saab carmaker')

    def test_dateline(self):
        self.assertEquals(self.item.get('dateline'), 'STOCKHOLM, Aug 29, 2014 (AFP) -')

    def test_slugline(self):
        self.assertEquals(self.item.get('slugline'), 'Sweden-SAAB')

    def test_byline(self):
        self.assertEquals(self.item.get('byline'), '')

    def test_language(self):
        self.assertEquals(self.item.get('language'), 'en')

    def test_guid(self):
        self.assertEquals(self.item.get('guid'), 'urn:newsml:afp.com:20140829T135002Z:TX-PAR-FXW86:1')

    def test_coreitemvalues(self):
        self.assertEquals(self.item.get('type'), 'text')
        self.assertEquals(self.item.get('urgency'), '4')
        self.assertEquals(self.item.get('version'), '1')
        self.assertEquals(self.item.get('versioncreated'), datetime.datetime(2014, 8, 29, 13, 49, 51))
        self.assertEquals(self.item.get('firstcreated'), datetime.datetime(2014, 8, 29, 13, 49, 51))
        self.assertEquals(self.item.get('pubstatus'), 'Usable')

    def test_subjects(self):
        self.assertEquals(len(self.item.get('subject')), 5)
        self.assertIn({'name': 'automotive equipment', 'qcode': '04011002'}, self.item.get('subject'))
        self.assertIn({'name': 'bankruptcy', 'qcode': '04016007'}, self.item.get('subject'))
        self.assertIn({'name': 'economy, business and finance', 'qcode': '04000000'}, self.item.get('subject'))
        self.assertIn({'name': 'quarterly or semiannual financial statement', 'qcode': '04016038'},
                      self.item.get('subject'))
        self.assertIn({'name': 'manufacturing and engineering', 'qcode': '04011000'}, self.item.get('subject'))

    def test_usageterms(self):
        self.assertEquals(self.item.get('usageterms'), 'NO ARCHIVAL USE')

    def test_genre(self):
        self.assertIn({'name': 'business'}, self.item.get('genre'))
        self.assertIn({'name': 'bankruptcy'}, self.item.get('genre'))

if __name__ == '__main__':
    unittest.main()
