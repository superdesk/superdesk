
import os
import unittest
from superdesk.etree import etree
from superdesk.io.nitf import NITFParser


class TestCase(unittest.TestCase):

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', 'aap.xml')
        with open(fixture) as f:
            self.nitf = f.read()
            self.item = NITFParser().parse_message(etree.fromstring(self.nitf))

    def test_headline(self):
        self.assertEquals(self.item.get('headline'), "The main stories on today's 1900 ABC TV news")

    def test_keywords(self):
        self.assertEquals(self.item.get('slugline'), 'Monitor 1900 ABC News')

    def test_subjects(self):
        self.assertEquals(len(self.item.get('subject')), 2)
        self.assertIn({'name': 'Justice'}, self.item.get('subject'))
        self.assertIn({'qcode': '02003000', 'name': 'Police'}, self.item.get('subject'))

    def test_guid(self):
        self.assertEquals(self.item.get('guid'), 'AAP.115314987.5417374')
        self.assertEquals(self.item.get('guid'), self.item.get('uri'))

    def test_type(self):
        self.assertEquals(self.item.get('type'), 'text')

    def test_urgency(self):
        self.assertEquals(self.item.get('urgency'), '5')

    def test_dateline(self):
        self.assertEquals(self.item.get('dateline'), 'Sydney')

    def test_byline(self):
        self.assertEquals(self.item.get('byline'), 'By John Doe')

    def test_abstract(self):
        self.assertEquals(self.item.get('abstract'), 'The main stories on today\'s 1900 ABC TV news')

    # def test_copyright(self):
    #     self.assertEquals(self.item.get('copyrightholder'), 'Australian Associated Press')

    def test_dates(self):
        self.assertEquals(self.item.get('firstcreated').isoformat(), '2013-10-20T19:27:51')
        self.assertEquals(self.item.get('versioncreated').isoformat(), '2013-10-20T19:27:51')

    def test_content(self):
        text = "<p>   1A) More extreme weather forecast over the next few days the <br />fire situation is likely"
        self.assertIn(text, self.item.get('body_html'))

    def test_pubstatus(self):
        self.assertEquals('usable', self.item.get('pubstatus'))

    def test_ingest_provider_sequence(self):
        self.assertEquals(self.item.get('ingest_provider_sequence'), '1747')

    def test_anpa_category(self):
        self.assertEquals(self.item.get('anpa-category')['qcode'], 'a')

if __name__ == '__main__':
    unittest.main()
