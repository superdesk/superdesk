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
import datetime
from superdesk.utc import utc
from superdesk.etree import etree
from superdesk.io.wenn_parser import WENNParser


class WENNTestCase(unittest.TestCase):
    filename = 'wenn.xml'

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', self.filename)
        provider = {'name': 'Wenn'}
        with open(fixture) as f:
            self.file = f.read()
            etree.fromstring(self.file)
            self.items = WENNParser().parse_message(etree.fromstring(self.file), provider)

    def test_items_counts(self):
        self.assertEqual(len(self.items), 2)

    def test_headline(self):
        self.assertEqual(self.items[0].get('headline'), 'Suge Knight involved in fatal hit and run incident')
        self.assertEqual(self.items[1].get('headline'), 'Jagged Edge singer Kyle Norman arrested over domestic assault')

    def test_abstract(self):
        self.assertEqual(self.items[0].get('abstract'),
                         'Police officials in Los Angeles are investigating a fatal hit and run incident involving '
                         'rap mogul SUGE KNIGHT on Thursday (29Jan15).')
        self.assertEqual(self.items[1].get('abstract'),
                         'JAGGED EDGE singer KYLE NORMAN has been arrested by police in Atlanta, Georgia amid'
                         ' allegations of aggravated assault.')

    def test_anpa_category(self):
        self.assertEqual(self.items[0].get('anpa_category')[0]['qcode'], 'e')
        self.assertEqual(self.items[1].get('anpa_category')[0]['qcode'], 'e')

    def test_subject(self):
        self.assertEqual(self.items[0].get('subject')[0]['qcode'], '01000000')
        self.assertEqual(self.items[1].get('subject')[0]['qcode'], '01000000')

    def test_firstcreated(self):
        self.assertEqual(self.items[0].get('firstcreated'), datetime.datetime(year=2015, month=1, day=30, hour=0,
                                                                              minute=33, second=6, tzinfo=utc))

    def test_versioncreated(self):
        self.assertEqual(self.items[0].get('versioncreated'), datetime.datetime(year=2015, month=1, day=30, hour=2,
                                                                                minute=40, second=56, tzinfo=utc))

    def test_body(self):
        self.assertEqual(self.items[0].get('body_html'), 'This is body content1.')
        self.assertEqual(self.items[1].get('body_html'), 'This is body content2.')

    def test_item_defaults(self):
        self.assertEqual(self.items[0].get('pubstatus'), 'usable')
        self.assertEqual(self.items[0].get('urgency'), 5)
        self.assertEqual(self.items[0].get('type'), 'text')

    def test_guid(self):
        self.assertEqual(self.items[0].get('guid'), '1369426')
        self.assertEqual(self.items[1].get('guid'), '1369417')

    def test_keywords(self):
        self.assertListEqual(self.items[0].get('keywords'), ['Suge Knight', 'Tmz.Com', 'Compton'])
        self.assertListEqual(self.items[1].get('keywords'),
                             ['Jagged Edge', 'Where The Party At', 'Usmagazine.Com', 'Kyle Norman'])
