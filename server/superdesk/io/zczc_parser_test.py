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
from superdesk.io.zczc import ZCZCParser


class ZCZCTestCase(unittest.TestCase):
    filename = 'Standings__2014_14_635535729050675896.tst'

    def setUp(self):
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.join(dirname, 'fixtures', self.filename)
        self.items = ZCZCParser().parse_file(fixture, self)

    def test_headline(self):
        self.assertEqual(self.items.get('headline'), 'MOTOR:  Collated results/standings after Sydney NRMA 500')

    def test_anpa_category(self):
        self.assertEqual(self.items.get('anpa_category')[0]['qcode'], 'T')

    def test_subject(self):
        self.assertEqual(self.items.get('subject')[0]['qcode'], '15039001')

    def test_version_created(self):
        self.assertIn('versioncreated', self.items)
