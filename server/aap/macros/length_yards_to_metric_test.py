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
from .length_yards_to_metric import yards_to_metric


class YardTestCase(unittest.TestCase):

    def test_y_to_m(self):
        text = 'Tom runs 125 yd in 11 seconds. ' \
               'Tom runs 125 yards in 11 seconds. ' \
               'Tom runs 125 Yards in 11 seconds. ' \
               'Tom runs 125-Yards in 11 seconds. ' \
               'Tom runs 12.5 yd in 11 seconds. ' \
               'Tom runs 12,500 yards in 11 seconds. ' \
               'Tom runs 100-12500 Yards in 11 seconds. ' \

        item = {'body_html': text}
        res, diff = yards_to_metric(item)
        self.assertEqual(diff['125 yd'], '125 yd (114 meters)')
        self.assertEqual(diff['125 yards'], '125 yards (114 meters)')
        self.assertEqual(diff['125 Yards'], '125 Yards (114 meters)')
        self.assertEqual(diff['125-Yards'], '125-Yards (114 meters)')
        self.assertEqual(diff['12.5 yd'], '12.5 yd (11.4 meters)')
        self.assertEqual(diff['12,500 yards'], '12,500 yards (11,430 meters)')
        self.assertEqual(diff['100-12500 Yards'], '100-12500 Yards (91-11,430 meters)')
