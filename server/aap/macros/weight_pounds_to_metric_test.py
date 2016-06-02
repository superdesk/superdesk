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
from .weight_pounds_to_metric import pounds_to_metric


class VolumeTestCase(unittest.TestCase):

    def test(self):
        text = 'Total volume is 100.50 pounds for this land. '\
               'Total volume is 15.7 lbs. for this land. '\
               'Total volume is 1 Pound for this land. '\
               'Total volume is 1-16 lb for this land. '\
               'Total volume is 1-16 lbs for this land. '\
               'Total volume is 16.7-pound for this land. '\
               'Total volume is 16,500-lb. for this land. '\

        item = {'body_html': text}
        res, diff = pounds_to_metric(item)
        self.assertEqual(diff['100.50 pounds'], '100.50 pounds (45.59 kg)')
        self.assertEqual(diff['15.7 lbs'], '15.7 lbs (7.1 kg)')
        self.assertEqual(diff['1 Pound'], '1 Pound (0.45 kg)')
        self.assertEqual(diff['1-16 lb'], '1-16 lb (0.45-7 kg)')
        self.assertEqual(diff['1-16 lbs'], '1-16 lbs (0.45-7 kg)')
        self.assertEqual(diff['16.7-pound'], '16.7-pound (7.6 kg)')
        self.assertEqual(diff['16,500-lb'], '16,500-lb (7,484 kg)')
