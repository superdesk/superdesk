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

from superdesk.io.iptc7901 import Iptc7901FileParser


def fixture(filename):
    dirname = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dirname, 'fixtures', filename)


class IptcTestCase(unittest.TestCase):

    parser = Iptc7901FileParser()

    def open(self, filename):
        return self.parser.parse_file(fixture(filename))

    def test_open_iptc7901_file(self):
        item = self.open('IPTC7901.txt')
        self.assertEqual('preformatted', item['type'])
        self.assertEqual('062', item['ingest_provider_sequence'])
        self.assertEqual('i', item['anpa_category'][0]['qcode'])
        self.assertEqual(211, item['word_count'])
        self.assertEqual('Germany Social Democrats: Coalition talks with Merkel could fail =', item['headline'])
        self.assertRegex(item['body_html'], '^\n   Berlin')
        self.assertEqual('Germany-politics', item['slugline'])
        self.assertEquals('R', item['priority'])
        self.assertEquals([{'qcode': 'i'}], item['anpa_category'])
