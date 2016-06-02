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
from .area_acre_to_metric import acre_to_metric


class TemperatureTestCase(unittest.TestCase):

    def test_f_to_c(self):
        text = 'Total area is 100.50 ac. for this land. '\
               'Total area is 15.7 Acres for this land. '\
               'Total area is 1 acre for this land. '\
               'Total area is 1-16 acres for this land. '\
               'Total area is 16.7-acres for this land. '\
               'Total area is 16,500-acre for this land. '\

        item = {'body_html': text}
        res, diff = acre_to_metric(item)
        self.assertEqual(diff['100.50 ac'], '100.50 ac (40.7 ha)')
        self.assertEqual(diff['15.7 Acres'], '15.7 Acres (6.4 ha)')
        self.assertEqual(diff['1 acre'], '1 acre (4,047 square meter)')
        self.assertEqual(diff['1-16 acres'], '1-16 acres (0.4-6.5 ha)')
        self.assertEqual(diff['16.7-acres'], '16.7-acres (6.8 ha)')
        self.assertEqual(diff['16,500-acre'], '16,500-acre (6,677 ha)')
