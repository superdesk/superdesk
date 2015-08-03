# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
import unittest

from superdesk.etree import etree, get_word_count
from superdesk.io import get_xml_parser

from .newsml_1_2 import NewsMLOneParser
from .newsml_2_0 import NewsMLTwoParser
from .nitf import NITFParser


def get_etree(filename):
    dirname = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dirname, 'fixtures', filename)) as f:
        return etree.fromstring(f.read().encode('utf-8'))


class UtilsTest(unittest.TestCase):

    def test_get_word_count(self):
        self.assertEqual(2, get_word_count('plain text'), 'plain text')
        self.assertEqual(2, get_word_count('<p> html text </p>'), 'paragraph')

        self.assertEqual(22, get_word_count(
            '<doc><p xml:lang="en-US">The weather was superb today in Norfolk, Virginia. Made me want to take\n'
            'out my boat, manufactured by the <org value="acm" idsrc="iptc.org">Acme Boat Company</org>.</p></doc>'))

    def test_get_xml_parser_newsmlg2(self):
        etree = get_etree('snep.xml')
        self.assertIsInstance(get_xml_parser(etree), NewsMLTwoParser)

    def test_get_xml_parser_nitf(self):
        etree = get_etree('nitf-fishing.xml')
        self.assertIsInstance(get_xml_parser(etree), NITFParser)

    def test_get_xml_parser_newsml12(self):
        etree = get_etree('afp.xml')
        self.assertIsInstance(get_xml_parser(etree), NewsMLOneParser)


class ItemTest(unittest.TestCase):

    def setUpFixture(self, filename):
        self.tree = get_etree(filename)
        provider = {'name': 'Test'}
        self.item = get_xml_parser(self.tree).parse_message(self.tree, provider)[0]


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
        self.assertEquals("2013-03-01T15:09:04", self.item.get('versioncreated').isoformat())
        self.assertEquals("2013-03-01T15:09:04", self.item.get('firstcreated').isoformat())
        self.assertEquals("Editorial Note", self.item.get('ednote'))

    def test_parse_content_meta(self):
        self.assertEquals('3', self.item.get('urgency'))
        self.assertEquals("SOCCER-ENGLAND/CHELSEA-BENITEZ", self.item["slugline"])
        self.assertEquals("Soccer-Smiling Benitez pleads for support "
                          "after midweek outburst against opponent", self.item["headline"])
        # self.assertEquals("Reuters", self.item["creditline"])
        self.assertEquals("Bangalore", self.item.get("dateline", {}).get('located', {}).get('city'))
        self.assertEquals("SOCCER-ENGLAND/CHELSEA-BENITEZ:Soccer-Smiling Benitez pleads for support after midweek outburst", self.item.get('description'))  # noqa

    # def test_parse_rights_info(self):
    #     self.assertEquals("Thomson Reuters", self.item.get('copyrightholder'))
    #     self.assertEquals("(c) Copyright Thomson Reuters 2013. Click For Restrictions - http://about.reuters.com/fulllegal.asp", self.item.get('copyrightnotice'))  # noqa

    def test_content_set(self):
        self.assertEqual("<p>By Toby Davis</p>", self.item.get('body_html'))
        self.assertEqual(569, self.item.get('word_count'))
        self.assertIsInstance(self.item.get('body_html'), type(''))

    def test_language(self):
        self.assertEquals('en', self.item.get('language'))

    def test_subject(self):
        self.assertEquals(2, len(self.item.get('subject')))
        self.assertIn({'qcode': '15054000', 'name': 'soccer'}, self.item.get('subject'))

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
        self.assertEquals("At least 15 killed on Kenya coast on election day", ref.get('headline'))
