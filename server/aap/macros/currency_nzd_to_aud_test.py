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
from .currency_nzd_to_aud import nzd_to_aud
from decimal import Decimal


class CurrencyTestCase(unittest.TestCase):

    def test_nzd_to_aud(self):
        text = 'This is a NZ$ 40 note. ' \
               'This is a NZ$41 note. ' \
               'This is a NZ$(42) note. ' \
               'This is a NZ$46,483 note. ' \
               'This is a NZ$4,648,382 note. ' \
               'This is a NZ$4,648,382.20 ' \
               'NZ$4,648,382.2 only ' \
               'This is (NZ$4,648,382.2) only ' \
               'This is NZ$4,648,820.20 only ' \
               'NZ$46,483 only ' \
               'This is NZ$(46.00) only ' \
               'This is a  NZD 52 note. ' \
               'This is a  NZD53 note. ' \
               'This is a  NZD(54,000) note. ' \
               'This is a  NZD (55,233.00) note. ' \

        item = {'body_html': text}
        res, diff = nzd_to_aud(item, rate=Decimal(2))
        self.assertEqual(diff['NZ$ 40'], 'NZ$ 40 ($A80)')
        self.assertEqual(diff['NZ$41'], 'NZ$41 ($A82)')
        self.assertEqual(diff['NZ$(42)'], 'NZ$(42) ($A84)')
        self.assertEqual(diff['NZ$46,483'], 'NZ$46,483 ($A92,966)')
        self.assertEqual(diff['NZ$4,648,382'], 'NZ$4,648,382 ($A9,296,764)')
        self.assertEqual(diff['NZ$4,648,382.20'], 'NZ$4,648,382.20 ($A9,296,764.40)')
        self.assertEqual(diff['NZD(54,000)'], 'NZD(54,000) ($A108,000)')
        self.assertEqual(diff['NZD 52'], 'NZD 52 ($A104)')
        self.assertEqual(diff['NZD53'], 'NZD53 ($A106)')
        self.assertEqual(diff['NZD (55,233.00)'], 'NZD (55,233.00) ($A110,466.00)')
