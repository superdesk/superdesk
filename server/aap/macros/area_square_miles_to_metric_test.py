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
from .area_square_miles_to_metric import square_mile_to_metric


class AreaTestCase(unittest.TestCase):

    def test_f_to_c(self):
        text = 'Total area is 100.50 square miles for this land. '\
               'Total area is 15.7 square mi for this land. '\
               'Total area is 1 Square Mile for this land. '\
               'Total area is 1-16 sq-mi for this land. '\
               'Total area is 16.7-Square-mi for this land. '\
               'Total area is 16,500-sq. mi for this land. '\

        item = {'body_html': text}
        res, diff = square_mile_to_metric(item)
        self.assertEqual(diff['100.50 square miles'], '100.50 square miles (260.3 square km)')
        self.assertEqual(diff['15.7 square mi'], '15.7 square mi (40.7 square km)')
        self.assertEqual(diff['1 Square Mile'], '1 Square Mile (259 ha)')
        self.assertEqual(diff['1-16 sq-mi'], '1-16 sq-mi (2.6-41.4 square km)')
        self.assertEqual(diff['16.7-Square-mi'], '16.7-Square-mi (43.3 square km)')
        self.assertEqual(diff['16,500-sq. mi'], '16,500-sq. mi (42,735 square km)')
