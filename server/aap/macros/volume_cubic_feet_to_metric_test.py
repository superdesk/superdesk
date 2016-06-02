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
from .volume_cubic_feet_to_metric import cubic_feet_to_metric


class VolumeTestCase(unittest.TestCase):

    def test(self):
        text = 'Total volume is 100.50 cubic feet for this land. '\
               'Total volume is 15.7 cubic ft for this land. '\
               'Total volume is 1 Cubic Foot for this land. '\
               'Total volume is 1-16 cu-ft for this land. '\
               'Total volume is 1-16 cb. ft for this land. '\
               'Total volume is 16.7-Cubic-ft for this land. '\
               'Total volume is 16,500-cu. ft. for this land. '\

        item = {'body_html': text}
        res, diff = cubic_feet_to_metric(item)
        self.assertEqual(diff['100.50 cubic feet'], '100.50 cubic feet (2.85 cubic meter)')
        self.assertEqual(diff['15.7 cubic ft'], '15.7 cubic ft (0.4 cubic meter)')
        self.assertEqual(diff['1 Cubic Foot'], '1 Cubic Foot (0.03 cubic meter)')
        self.assertEqual(diff['1-16 cu-ft'], '1-16 cu-ft (0.03-0.45 cubic meter)')
        self.assertEqual(diff['1-16 cb. ft'], '1-16 cb. ft (0.03-0.45 cubic meter)')
        self.assertEqual(diff['16.7-Cubic-ft'], '16.7-Cubic-ft (0.5 cubic meter)')
        self.assertEqual(diff['16,500-cu. ft'], '16,500-cu. ft (467 cubic meter)')
