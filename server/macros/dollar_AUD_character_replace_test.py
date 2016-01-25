# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import unittest
from macros.dollar_AUD_character_replace import find_and_replace


class DollarAUDReplaceTestCase(unittest.TestCase):

    def setUp(self):
        self.body = ("Cost of train tickets increased by $1 for all destinations")

    def test_replace_body(self):
        item = {'body_html': self.body}
        item = find_and_replace(item)
        self.assertEqual(item['body_html'], 'Cost of train tickets increased by AUD 1 for all destinations')

    def test_replace_abstract(self):
        item = {'abstract': self.body}
        item = find_and_replace(item)
        self.assertEqual(item['abstract'], 'Cost of train tickets increased by AUD 1 for all destinations')

    def test_replace_headline(self):
        item = {'headline': self.body}
        item = find_and_replace(item)
        self.assertEqual(item['headline'], 'Cost of train tickets increased by AUD 1 for all destinations')

    def test_replace_slugline(self):
        item = {'slugline': self.body}
        item = find_and_replace(item)
        self.assertEqual(item['slugline'], 'Cost of train tickets increased by AUD 1 for all destinations')
