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
from .currency_chf_to_aud import chf_to_aud
from decimal import Decimal


class CurrencyTestCase(unittest.TestCase):

    def test_chf_to_aud(self):
        text = 'This is a Fr 40 note. ' \
               'This is a Fr41 note. ' \
               'This is a Fr(42) note. ' \
               'This is a Fr46,483 note. ' \
               'This is a Fr4,648,382 note. ' \
               'This is a Fr4,648,382.20 ' \
               'This is a  CHF 52 note. ' \
               'This is a  CHF53 note. ' \
               'This is a  CHF(54,000) note. ' \
               'This is a  CHF (55,233.00) note. ' \

        item = {'body_html': text}
        res, diff = chf_to_aud(item, rate=Decimal(2))
        self.assertEqual(diff['Fr 40'], 'Fr 40 ($A80)')
        self.assertEqual(diff['Fr41'], 'Fr41 ($A82)')
        self.assertEqual(diff['Fr(42)'], 'Fr(42) ($A84)')
        self.assertEqual(diff['Fr46,483'], 'Fr46,483 ($A92,966)')
        self.assertEqual(diff['Fr4,648,382'], 'Fr4,648,382 ($A9,296,764)')
        self.assertEqual(diff['Fr4,648,382.20'], 'Fr4,648,382.20 ($A9,296,764.40)')
        self.assertEqual(diff['CHF(54,000)'], 'CHF(54,000) ($A108,000)')
        self.assertEqual(diff['CHF 52'], 'CHF 52 ($A104)')
        self.assertEqual(diff['CHF53'], 'CHF53 ($A106)')
        self.assertEqual(diff['CHF (55,233.00)'], 'CHF (55,233.00) ($A110,466.00)')
