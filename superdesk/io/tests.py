from __future__ import unicode_literals

import os
import xml.etree.ElementTree as etree

import unittest

import superdesk.models as models
import superdesk.io.newsml as newsml

class ItemTest(unittest.TestCase):

    def setUpFixture(self, filename):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', filename)
        xml = etree.parse(fixture)
        parser = newsml.Parser()
        self.item = parser.parse_message(xml)[0]

class TextParserTest(ItemTest):
    def setUp(self):
        self.setUpFixture('text.xml')

    def test_instance(self):
        self.assertTrue(isinstance(self.item, models.Item))

    def test_parse_id(self):
        self.assertEquals("tag:reuters.com,0000:newsml_L4N0BT5PJ", self.item.guid)
        self.assertEquals(263518268, self.item.version)

    def test_parse_item_meta(self):
        self.assertEquals("icls:text", self.item.itemClass)
        self.assertEquals("reuters.com", self.item.provider)
        self.assertEquals("2013-03-01T15:09:04", self.item.versionCreated.isoformat())
        self.assertEquals("2013-03-01T15:09:04", self.item.firstCreated.isoformat())

    def test_parse_content_meta(self):
        self.assertEquals("3", self.item.urgency)
        self.assertEquals("SOCCER-ENGLAND/CHELSEA-BENITEZ", self.item["slugline"])
        self.assertEquals("Soccer-Smiling Benitez pleads for support after midweek outburst", self.item["headline"])
        self.assertEquals("Reuters", self.item["creditline"])
        self.assertEquals("SOCCER-ENGLAND/CHELSEA-BENITEZ:Soccer-Smiling Benitez pleads for support after midweek outburst", self.item.description)

    def test_parse_rights_info(self):
        self.assertEquals("Thomson Reuters", self.item.copyrightHolder)
        self.assertEquals("(c) Copyright Thomson Reuters 2013. Click For Restrictions - http://about.reuters.com/fulllegal.asp", self.item.copyrightNotice)

    def test_content_set(self):
        content = self.item['contents'][0]
        self.assertTrue(isinstance(content, models.Content))
        self.assertEquals("application/xhtml+html", content.contenttype)
        self.assertIn("<p>By Toby Davis</p>", content.content)

class PictureParserTest(ItemTest):
    def setUp(self):
        self.setUpFixture('picture.xml')

    def test_content_set(self):
        self.assertEquals(3, len(self.item.contents))

        remote = self.item.contents[0]
        self.assertTrue(isinstance(remote, models.Content))
        self.assertEquals("tag:reuters.com,0000:binary_GM1E9341HD701-BASEIMAGE", remote.residRef)
        self.assertEquals(772617, remote.size)
        self.assertEquals("rend:baseImage", remote.rendition)
        self.assertEquals("image/jpeg", remote.contenttype)
        self.assertEquals("http://content.reuters.com/auth-server/content/tag:reuters.com,0000:newsml_GM1E9341HD701:360624134/tag:reuters.com,0000:binary_GM1E9341HD701-BASEIMAGE", remote.href)

class SNEPParserTest(ItemTest):
    def setUp(self):
        self.setUpFixture('snep.xml')

    def test_content_set(self):
        self.assertEquals(2, len(self.item.groups))

        group = self.item.groups[0]
        self.assertTrue(isinstance(group, models.Group))
        self.assertEquals("root", group.id)
        self.assertEquals("grpRole:SNEP", group.role)
        self.assertEquals(1, len(group.refs))
        self.assertEquals("main", group.refs[0].idRef)

        group = self.item.groups[1]
        self.assertEquals(10, len(group.refs))
        self.assertEquals("main", group.id)

        ref = group.refs[0]
        self.assertTrue(isinstance(ref, models.Ref))
        self.assertEquals("tag:reuters.com,0000:newsml_BRE9220HA", ref.residRef)
        self.assertEquals("application/vnd.iptc.g2.packageitem+xml", ref.contentType)
        self.assertEquals("icls:composite", ref.itemClass)
        self.assertEquals("reuters.com", ref.provider)
        self.assertEquals("At least 15 killed on Kenya coast on election day", ref.headline)
