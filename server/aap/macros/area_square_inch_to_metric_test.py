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
from .area_square_inch_to_metric import square_inch_to_metric


class AreaTestCase(unittest.TestCase):

    def test_f_to_c(self):
        text = 'Total area is 100.50 square inches for this land. '\
               'Total area is 15.7 square in for this land. '\
               'Total area is 1 Square Inch for this land. '\
               'Total area is 1-16 sq-in for this land. '\
               'Total area is 16.7-Square-in for this land. '\
               'Total area is 16,500-sq. in for this land. '\

        item = {'body_html': text}
        res, diff = square_inch_to_metric(item)
        self.assertEqual(diff['100.50 square inches'], '100.50 square inches (648.39 square cm)')
        self.assertEqual(diff['15.7 square in'], '15.7 square in (101.29 square cm)')
        self.assertEqual(diff['1 Square Inch'], '1 Square Inch (6.45 square cm)')
        self.assertEqual(diff['1-16 sq-in'], '1-16 sq-in (6.45-103.23 square cm)')
        self.assertEqual(diff['16.7-Square-in'], '16.7-Square-in (107.74 square cm)')
        self.assertEqual(diff['16,500-sq. in'], '16,500-sq. in (10.6 square meter)')
