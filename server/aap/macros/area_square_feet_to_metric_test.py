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
from .area_square_feet_to_metric import square_feet_to_metric


class AreaTestCase(unittest.TestCase):

    def test_f_to_c(self):
        text = 'Total area is 100.50 square feet for this land. '\
               'Total area is 15.7 square ft for this land. '\
               'Total area is 1 Square Foot for this land. '\
               'Total area is 1-16 sq-ft for this land. '\
               'Total area is 16.7-Square-ft for this land. '\
               'Total area is 16,500-sq. ft for this land. '\

        item = {'body_html': text}
        res, diff = square_feet_to_metric(item)
        self.assertEqual(diff['100.50 square feet'], '100.50 square feet (9.3 square meter)')
        self.assertEqual(diff['15.7 square ft'], '15.7 square ft (1.5 square meter)')
        self.assertEqual(diff['1 Square Foot'], '1 Square Foot (0.1 square meter)')
        self.assertEqual(diff['1-16 sq-ft'], '1-16 sq-ft (0.1-1.5 square meter)')
        self.assertEqual(diff['16.7-Square-ft'], '16.7-Square-ft (1.6 square meter)')
        self.assertEqual(diff['16,500-sq. ft'], '16,500-sq. ft (1,533 square meter)')
