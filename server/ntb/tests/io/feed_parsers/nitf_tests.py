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
import settings
from superdesk import config
from superdesk.tests import TestCase

from superdesk.etree import etree
from superdesk.io.feed_parsers.nitf import NITFFeedParser


class NITFTestCase(TestCase):

    def setUp(self):
        super().setUp()
        for key in dir(settings):
            if key.isupper():
                setattr(config, key, getattr(settings, key))
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        provider = {'name': 'Test'}
        with open(fixture) as f:
            self.nitf = f.read()
            self.item = NITFFeedParser().parse(etree.fromstring(self.nitf), provider)


class NTBTestCase(NITFTestCase):

    filename = 'nitf_test.xml'

    def test_category(self):
        self.assertEqual(self.item.get('anpa_category'), [{'qcode': 'Utenriks', 'name': 'Utenriks'}])

    def test_genre(self):
        self.assertEqual(self.item.get('genre'), [{'qcode': 'Nyheter', 'name': 'Nyheter'}])

    def test_slugline(self):
        self.assertEqual(self.item.get('slugline'), "NU-FLASH-K")

    def test_abstract(self):
        self.assertEqual(
            self.item.get('abstract'),
            "København /ritzau/: "
            "En 41-årig mand, der onsdag blev anholdt og sat i forbindelse "
            "med en mulig skudepisode nær en børnehave i Hvidovre ved København, "
            "er blevet løsladt.")

    def test_keywords(self):
        self.assertNotIn('keywords', self.item)
        self.assertEqual(self.item.get('guid'), self.item.get('uri'))
