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
from .volume_cubic_yard_to_metric import cubic_yard_to_metric


class VolumeTestCase(unittest.TestCase):

    def test(self):
        text = 'Total volume is 100.50 cubic yards for this land. '\
               'Total volume is 15.7 cubic yds for this land. '\
               'Total volume is 1 Cubic Yard for this land. '\
               'Total volume is 1-16 cu-yd for this land. '\
               'Total volume is 1-16 cb. yds for this land. '\
               'Total volume is 16.7-Cubic-yd for this land. '\
               'Total volume is 16,500-cu. yd. for this land. '\

        item = {'body_html': text}
        res, diff = cubic_yard_to_metric(item)
        self.assertEqual(diff['100.50 cubic yards'], '100.50 cubic yards (76.84 cubic meter)')
        self.assertEqual(diff['15.7 cubic yds'], '15.7 cubic yds (12.0 cubic meter)')
        self.assertEqual(diff['1 Cubic Yard'], '1 Cubic Yard (0.76 cubic meter)')
        self.assertEqual(diff['1-16 cu-yd'], '1-16 cu-yd (0.76-12 cubic meter)')
        self.assertEqual(diff['1-16 cb. yds'], '1-16 cb. yds (0.76-12 cubic meter)')
        self.assertEqual(diff['16.7-Cubic-yd'], '16.7-Cubic-yd (12.8 cubic meter)')
        self.assertEqual(diff['16,500-cu. yd'], '16,500-cu. yd (12,615 cubic meter)')
