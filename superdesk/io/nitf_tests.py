
import os
import unittest

from .nitf import parse


class TestCase(unittest.TestCase):

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', 'aap.xml')
        with open(fixture) as f:
            self.nitf = f.read()
            self.item = parse(self.nitf)

    def test_headline(self):
        self.assertEquals(self.item.get('headline'), "The main stories on today's 1900 ABC TV news")

    def test_keywords(self):
        self.assertEquals(self.item.get('keywords'), ['Monitor 1900 ABC News'])

    def test_subjects(self):
        self.assertEquals(len(self.item.get('subject')), 2)
        self.assertIn({'qcode': '02000000', 'name': 'crime, law and justice'}, self.item.get('subject'))
        self.assertIn({'qcode': '02003000', 'name': 'police'}, self.item.get('subject'))

    def test_guid(self):
        self.assertEquals(self.item.get('guid'), 'AAP.115314987.5417374')
        self.assertEquals(self.item.get('guid'), self.item.get('uri'))

    def test_type(self):
        self.assertEquals(self.item.get('type'), 'text')

    def test_urgency(self):
        self.assertEquals(self.item.get('urgency'), '5')

    def test_copyright(self):
        self.assertEquals(self.item.get('copyrightHolder'), 'Australian Associated Press')

    def test_dates(self):
        self.assertEquals(self.item.get('firstcreated').isoformat(), '2013-10-20T19:27:51')
        self.assertEquals(self.item.get('versioncreated').isoformat(), '2013-10-20T19:27:51')

    def test_content(self):
        text = "<p>   1A) More extreme weather forecast over the next few days the <br />fire situation is likely"
        self.assertIn(text, self.item.get('body_html'))

    def test_rights_info(self):
        self.assertTrue(self.item.get('rightsInfo'))

if __name__ == '__main__':
    unittest.main()
