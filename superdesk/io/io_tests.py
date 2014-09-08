import os
import unittest
from superdesk.etree import etree
import test

from superdesk.io import newsml_2_0


class ItemTest(unittest.TestCase):

    def setUpFixture(self, filename):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', filename)
        with open(fixture) as f:
            self.tree = etree.fromstring(f.read().encode('utf-8'))
        parser = newsml_2_0.Parser()
        self.item = parser.parse_message(self.tree)[0]


class TextParserTest(ItemTest):
    def setUp(self):
        self.setUpFixture('text.xml')

    def test_instance(self):
        self.assertTrue(self.item)

    def test_parse_id(self):
        self.assertEquals("tag:reuters.com,0000:newsml_L4N0BT5PJ", self.item.get('guid'))
        self.assertEquals('263518268', self.item.get('version'))
        self.assertEquals(self.item.get('guid'), self.item.get('uri'))

    def test_parse_item_meta(self):
        self.assertEquals("text", self.item.get('type'))
        self.assertEquals("reuters.com", self.item.get('provider'))
        self.assertEquals("2013-03-01T15:09:04", self.item.get('versioncreated').isoformat())
        self.assertEquals("2013-03-01T15:09:04", self.item.get('firstcreated').isoformat())

    def test_parse_content_meta(self):
        self.assertEquals('3', self.item.get('urgency'))
        self.assertEquals("SOCCER-ENGLAND/CHELSEA-BENITEZ", self.item["slugline"])
        self.assertEquals("Soccer-Smiling Benitez pleads for support after midweek outburst", self.item["headline"])
        self.assertEquals("Reuters", self.item["creditline"])
        self.assertEquals("SOCCER-ENGLAND/CHELSEA-BENITEZ:Soccer-Smiling Benitez pleads for support after midweek outburst", self.item.get('description_text'))  # noqa

    def test_parse_rights_info(self):
        self.assertEquals("Thomson Reuters", self.item.get('copyrightholder'))
        self.assertEquals("(c) Copyright Thomson Reuters 2013. Click For Restrictions - http://about.reuters.com/fulllegal.asp", self.item.get('copyrightnotice'))  # noqa

    def test_content_set(self):
        self.assertEquals("<p>By Toby Davis</p>", self.item.get('body_html'))

    def test_language(self):
        self.assertEquals('en', self.item.get('language'))

    def test_subject(self):
        self.assertEquals(2, len(self.item.get('subject')))
        self.assertIn({'code': '15054000', 'name': 'soccer'}, self.item.get('subject'))

    def test_pubstatus(self):
        self.assertEquals('usable', self.item.get('pubstatus'))


class PictureParserTest(ItemTest):
    def setUp(self):
        self.setUpFixture('picture.xml')

    def test_type(self):
        self.assertEquals('picture', self.item.get('type'))

    def test_content_set(self):
        self.assertEquals(3, len(self.item.get('renditions')))

        remote = self.item.get('renditions').get('baseImage')
        self.assertTrue(remote)
        self.assertEquals("tag:reuters.com,0000:binary_GM1E9341HD701-BASEIMAGE", remote.get('residRef'))
        self.assertEquals(772617, remote.get('sizeinbytes'))
        self.assertEquals("image/jpeg", remote.get('mimetype'))
        self.assertEquals("http://content.reuters.com/auth-server/content/tag:reuters.com,0000:newsml_GM1E9341HD701:360624134/tag:reuters.com,0000:binary_GM1E9341HD701-BASEIMAGE", remote.get('href'))  # noqa

    def test_byline(self):
        self.assertEquals('MARKO DJURICA', self.item.get('byline'))

    def test_place(self):
        self.assertEquals(2, len(self.item.get('place')))
        self.assertIn({'name': 'NAIROBI'}, self.item['place'])
        self.assertIn({'name': 'Kenya'}, self.item['place'])


class SNEPParserTest(ItemTest):
    def setUp(self):
        self.setUpFixture('snep.xml')

    def test_content_set(self):
        self.assertEquals(2, len(self.item.get('groups')))

        group = self.item.get('groups')[0]
        self.assertTrue(group)
        self.assertEquals("root", group.get('id'))
        self.assertEquals("grpRole:SNEP", group.get('role'))
        self.assertEquals(1, len(group.get('refs')))
        self.assertEquals("main", group.get('refs')[0].get('idRef'))

        group = self.item.get('groups')[1]
        self.assertEquals(10, len(group.get('refs')))
        self.assertEquals("main", group.get('id'))

        ref = group.get('refs')[0]
        self.assertTrue(ref)
        self.assertEquals("tag:reuters.com,0000:newsml_BRE9220HA", ref.get('residRef'))
        self.assertEquals("application/vnd.iptc.g2.packageitem+xml", ref.get('contentType'))
        self.assertEquals("icls:composite", ref.get('itemClass'))
        self.assertEquals("reuters.com", ref.get('provider'))
        self.assertEquals("At least 15 killed on Kenya coast on election day", ref.get('headline'))

if __name__ == '__main__':
    test.drop_db()
    unittest.main()
