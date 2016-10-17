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
from superdesk.vocabularies.command import VocabulariesPopulateCommand

ABSTRACT = ("København /ritzau/: "
            "En 41-årig mand, der onsdag blev anholdt og sat i forbindelse "
            "med en mulig skudepisode nær en børnehave i Hvidovre ved København, "
            "er blevet løsladt.")


class NITFTestCase(TestCase):

    def setUp(self):
        super().setUp()
        # we need to prepopulate vocabularies to get qcodes
        voc_file = os.path.join(os.path.abspath(os.path.dirname(settings.__file__)), "data/vocabularies.json")
        VocabulariesPopulateCommand().run(voc_file)

        # settings are needed in order to get into account NITF_MAPPING
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

    def test_subject_update(self):
        self.assertEqual(len(self.item.get('subject')), 2)

    def test_category(self):
        self.assertIn({'qcode': 'Utenriks', 'name': 'Utenriks', 'scheme': 'category'}, self.item.get('subject'))

    def test_genre(self):
        self.assertEqual(self.item.get('genre'), [{'qcode': 'Nyheter', 'name': 'Nyheter', 'scheme': 'genre_custom'}])

    def test_slugline(self):
        self.assertEqual(self.item.get('slugline'), "NU-FLASH-K")

    def test_subject(self):
        self.assertIn({'qcode': '02000000', 'name': 'Kriminalitet og rettsvesen', 'scheme': 'subject_custom'},
                      self.item.get('subject'))

    def test_abstract(self):
        self.assertEqual(
            self.item.get('abstract'),
            ABSTRACT)

    def test_body_html(self):
        self.assertNotIn(ABSTRACT, self.item.get('body_html'))

    def test_keywords(self):
        self.assertNotIn('keywords', self.item)
        self.assertEqual(self.item.get('guid'), self.item.get('uri'))

    def test_service(self):
        self.assertEqual(self.item.get('anpa_category'),
                         [{'qcode': 'n', 'name': 'Nyhetstjenesten', 'language': 'nb-NO'}])

    def test_priority(self):
        self.assertEqual(self.item.get('priority'), 3)
