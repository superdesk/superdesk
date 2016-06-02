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
from .volume_cubic_inches_to_metric import cubic_inches_to_metric


class VolumeTestCase(unittest.TestCase):

    def test(self):
        text = 'Total volume is 100.50 cubic inches for this land. '\
               'Total volume is 15.7 cubic in for this land. '\
               'Total volume is 1 Cubic Inch for this land. '\
               'Total volume is 1-16 cu-in for this land. '\
               'Total volume is 1-16 cb. in for this land. '\
               'Total volume is 16.7-Cubic-in for this land. '\
               'Total volume is 16,500-cu. in. for this land. '\

        item = {'body_html': text}
        res, diff = cubic_inches_to_metric(item)
        self.assertEqual(diff['100.50 cubic inches'], '100.50 cubic inches (1,647 cubic centimeter)')
        self.assertEqual(diff['15.7 cubic in'], '15.7 cubic in (257.3 cubic centimeter)')
        self.assertEqual(diff['1 Cubic Inch'], '1 Cubic Inch (16 cubic centimeter)')
        self.assertEqual(diff['1-16 cu-in'], '1-16 cu-in (16-262 cubic centimeter)')
        self.assertEqual(diff['1-16 cb. in'], '1-16 cb. in (16-262 cubic centimeter)')
        self.assertEqual(diff['16.7-Cubic-in'], '16.7-Cubic-in (273.7 cubic centimeter)')
        self.assertEqual(diff['16,500-cu. in'], '16,500-cu. in (0.3 cubic meter)')
