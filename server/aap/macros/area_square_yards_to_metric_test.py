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
from .area_square_yards_to_metric import square_yard_to_metric


class TemperatureTestCase(unittest.TestCase):

    def test_f_to_c(self):
        text = 'Total area is 100.50 square yards for this land. '\
               'Total area is 15.7 square yds for this land. '\
               'Total area is 1 sq.yd for this land. '\
               'Total area is 1-16 sq-yds for this land. '\
               'Total area is 16.7-Square-yds for this land. '\
               'Total area is 16,500-Square Yards. for this land. '\

        item = {'body_html': text}
        res, diff = square_yard_to_metric(item)
        self.assertEqual(diff['100.50 square yards'], '100.50 square yards (84.03 square meter)')
        self.assertEqual(diff['15.7 square yds'], '15.7 square yds (13.1 square meter)')
        self.assertEqual(diff['1 sq.yd'], '1 sq.yd (0.84 square meter)')
        self.assertEqual(diff['1-16 sq-yds'], '1-16 sq-yds (0.84-13 square meter)')
        self.assertEqual(diff['16.7-Square-yds'], '16.7-Square-yds (14.0 square meter)')
        self.assertEqual(diff['16,500-Square Yards'], '16,500-Square Yards (1.4 ha)')
