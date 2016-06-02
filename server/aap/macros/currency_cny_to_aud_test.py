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
from .currency_cny_to_aud import yuan_to_aud
from decimal import Decimal


class CurrencyTestCase(unittest.TestCase):

    def test_cny_to_aud(self):
        text = 'This is a ¥ 40 note. ' \
               'This is a ¥41 note. ' \
               'This is a CN¥(42) note. ' \
               'This is a CN¥46,483 note. ' \
               'This is a CN¥4,648,382 note. ' \
               'This is a ¥4,648,382.20 ' \
               '¥4,648,382.2 only ' \
               'This is (¥4,648,382.2) only ' \
               'This is ¥4,648,820.20 only ' \
               'CN¥46,483 only ' \
               'This is ¥(46.00) only ' \
               'This is a  CNY 52 note. ' \
               'This is a  CNY53 note. ' \
               'This is a  CNY(54,000) note. ' \
               'This is a  CNY (55,233.00) note. ' \
               'This is a  RMB 52 note. ' \
               'This is a  RMB53 note. ' \
               'This is a  RMB(54,000) note. ' \
               'This is a  RMB (55,233.00) note. ' \

        item = {'body_html': text}
        res, diff = yuan_to_aud(item, rate=Decimal(2))
        self.assertEqual(diff['¥ 40'], '¥ 40 ($A80)')
        self.assertEqual(diff['¥41'], '¥41 ($A82)')
        self.assertEqual(diff['CN¥(42)'], 'CN¥(42) ($A84)')
        self.assertEqual(diff['CN¥46,483'], 'CN¥46,483 ($A92,966)')
        self.assertEqual(diff['CN¥4,648,382'], 'CN¥4,648,382 ($A9,296,764)')
        self.assertEqual(diff['¥4,648,382.20'], '¥4,648,382.20 ($A9,296,764.40)')
        self.assertEqual(diff['CNY(54,000)'], 'CNY(54,000) ($A108,000)')
        self.assertEqual(diff['CNY 52'], 'CNY 52 ($A104)')
        self.assertEqual(diff['CNY53'], 'CNY53 ($A106)')
        self.assertEqual(diff['CNY (55,233.00)'], 'CNY (55,233.00) ($A110,466.00)')
        self.assertEqual(diff['RMB(54,000)'], 'RMB(54,000) ($A108,000)')
        self.assertEqual(diff['RMB 52'], 'RMB 52 ($A104)')
        self.assertEqual(diff['RMB53'], 'RMB53 ($A106)')
        self.assertEqual(diff['RMB (55,233.00)'], 'RMB (55,233.00) ($A110,466.00)')
