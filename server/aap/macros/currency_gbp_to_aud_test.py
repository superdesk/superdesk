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
from .currency_gbp_to_aud import gbp_to_aud
from decimal import Decimal


class CurrencyTestCase(unittest.TestCase):

    def test_gbp_to_aud(self):
        text = 'This is a £ 40 note. ' \
               'This is a £41 note. ' \
               'This is a £(42) note. ' \
               'This is a £46,483 note. ' \
               'This is a £4,648,382 note. ' \
               'This is a £4,648,382.20 ' \
               '£4,648,382.2 only ' \
               'This is (£4,648,382.2) only ' \
               'This is £4,648,820.20 only ' \
               '£46,483 only ' \
               'This is £(46.00) only ' \
               'This is a  GBP 52 note. ' \
               'This is a  GBP53 note. ' \
               'This is a  GBP(54,000) note. ' \
               'This is a  GBP (55,233.00) note. ' \
               'This is a  STG 52 note. ' \
               'This is a  STG53 note. ' \
               'This is a  STG(54,000) note. ' \
               'This is a  STG (55,233.00) note. ' \

        item = {'body_html': text}
        res, diff = gbp_to_aud(item, rate=Decimal(2))
        self.assertEqual(diff['£ 40'], '£ 40 ($A80)')
        self.assertEqual(diff['£41'], '£41 ($A82)')
        self.assertEqual(diff['£(42)'], '£(42) ($A84)')
        self.assertEqual(diff['£46,483'], '£46,483 ($A92,966)')
        self.assertEqual(diff['£4,648,382'], '£4,648,382 ($A9,296,764)')
        self.assertEqual(diff['£4,648,382.20'], '£4,648,382.20 ($A9,296,764.40)')
        self.assertEqual(diff['GBP(54,000)'], 'GBP(54,000) ($A108,000)')
        self.assertEqual(diff['STG 52'], 'STG 52 ($A104)')
        self.assertEqual(diff['STG53'], 'STG53 ($A106)')
        self.assertEqual(diff['STG (55,233.00)'], 'STG (55,233.00) ($A110,466.00)')
