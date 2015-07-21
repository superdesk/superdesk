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
from superdesk.etree import etree
from superdesk.io.nitf import NITFParser


class NITFTestCase(unittest.TestCase):

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', self.filename)
        provider = {'name': 'Test'}
        with open(fixture) as f:
            self.nitf = f.read()
            self.item = NITFParser().parse_message(etree.fromstring(self.nitf), provider)


class AAPTestCase(NITFTestCase):

    filename = 'aap.xml'

    def test_headline(self):
        self.assertEqual(self.item.get('headline'), "The main stories on today's 1900 ABC TV news")

    def test_slugline(self):
        self.assertEqual(self.item.get('slugline'), 'Monitor 1900 ABC News')

    def test_subjects(self):
        self.assertEqual(len(self.item.get('subject')), 2)
        self.assertIn({'name': 'Justice'}, self.item.get('subject'))
        self.assertIn({'qcode': '02003000', 'name': 'Police'}, self.item.get('subject'))

    def test_guid(self):
        self.assertEqual(self.item.get('guid'), 'AAP.115314987.5417374')
        self.assertEqual(self.item.get('guid'), self.item.get('uri'))

    def test_type(self):
        self.assertEqual(self.item.get('type'), 'text')

    def test_urgency(self):
        self.assertEqual(self.item.get('urgency'), 5)

    def test_dateline(self):
        self.assertEqual(self.item.get('dateline', {}).get('located', {}).get('city'), 'Sydney')

    def test_byline(self):
        self.assertEqual(self.item.get('byline'), 'By John Doe')

    def test_abstract(self):
        self.assertEqual(self.item.get('abstract'), 'The main stories on today\'s 1900 ABC TV news')

    def test_dates(self):
        self.assertEqual(self.item.get('firstcreated').isoformat(), '2013-10-20T08:27:51+00:00')
        self.assertEqual(self.item.get('versioncreated').isoformat(), '2013-10-20T08:27:51+00:00')

    def test_content(self):
        text = "<p>   1A) More extreme weather forecast over the next few days the <br />fire situation is likely"
        self.assertIn(text, self.item.get('body_html'))
        self.assertIsInstance(self.item.get('body_html'), type(''))
        self.assertNotIn('<body.content>', self.item.get('body_html'))

    def test_pubstatus(self):
        self.assertEqual('usable', self.item.get('pubstatus'))

    def test_ingest_provider_sequence(self):
        self.assertEqual(self.item.get('ingest_provider_sequence'), '1747')

    def test_anpa_category(self):
        self.assertEqual(self.item.get('anpa_category')[0]['qcode'], 'a')

    def test_word_count(self):
        self.assertEqual(349, self.item.get('word_count'))


class IPTCExampleTestCase(NITFTestCase):

    filename = 'nitf-fishing.xml'

    def test_headline(self):
        self.assertEqual(self.item.get('headline'), 'Weather and Tide Updates for Norfolk')

    def test_pubstatus(self):
        self.assertEqual('canceled', self.item.get('pubstatus'))

    def test_guid(self):
        self.assertEquals('iptc.321656141.b', self.item.get('guid'))

    def test_subjects(self):
        self.assertEqual(3, len(self.item.get('subject')))

    def test_place(self):
        places = self.item.get('place', [])
        self.assertEqual(1, len(places))
        self.assertEqual('Norfolk', places[0]['name'])
        self.assertEqual('US', places[0]['code'])

    def test_expiry(self):
        self.assertEqual('2012-02-26T14:30:00+00:00', self.item.get('expiry').isoformat())

    def test_keywords(self):
        self.assertIn('fishing', self.item.get('keywords'))

    def test_ednote(self):
        self.assertEqual('Today begins an expanded format of this popular column.', self.item.get('ednote'))

    def test_byline(self):
        self.assertEqual('By Alan Karben', self.item.get('byline'))

    def test_word_count(self):
        self.assertEqual(220, self.item.get('word_count'))
