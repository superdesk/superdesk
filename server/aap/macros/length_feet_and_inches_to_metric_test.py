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
from .length_feet_and_inches_to_metric import feet_inches_to_metric


class FeetInchesTestCase(unittest.TestCase):

    def test_feet_to_cm(self):
        text = '''His height is 5'10" today
               His height is 5'10 today
               His height is 5' 10 today
               His height is 5 ft 10 today
               His height is 5 ft. 10 today
               His height is 5 ft 10 in today
               His height is 5' 10" today
               His height is 5' today
               His height is 5 ft today
               His height is 5 feet today
               His height is 10.2-ft today
               His height is 10.2-in today
               His height is 1,020" today
               His height is 1,020 in today
               His height is 1 inch today
               His height is 1,020 inches today
               His height is 10-12 ft today
               His height is 10-12 in today'''

        item = {'body_html': text}
        res, diff = feet_inches_to_metric(item)
        self.assertEqual(diff['5\'10"'], '5\'10" (1.78 m)')
        self.assertEqual(diff['5\'10'], '5\'10 (1.78 m)')
        self.assertEqual(diff['5\' 10'], '5\' 10 (1.78 m)')
        self.assertEqual(diff['5 ft 10'], '5 ft 10 (1.78 m)')
        self.assertEqual(diff['5 ft. 10'], '5 ft. 10 (1.78 m)')
        self.assertEqual(diff['5 ft 10 in'], '5 ft 10 in (1.78 m)')
        self.assertEqual(diff['5\' 10"'], '5\' 10" (1.78 m)')
        self.assertEqual(diff['5\''], '5\' (1.52 m)')
        self.assertEqual(diff['5 ft'], '5 ft (1.52 m)')
        self.assertEqual(diff['5 feet'], '5 feet (1.52 m)')
        self.assertEqual(diff['10.2-ft'], '10.2-ft (3.11 m)')
        self.assertEqual(diff['10.2-in'], '10.2-in (25.91 cm)')
        self.assertEqual(diff['1,020"'], '1,020" (25.91 m)')
        self.assertEqual(diff['1,020 in'], '1,020 in (25.91 m)')
        self.assertEqual(diff['1 inch'], '1 inch (2.54 cm)')
        self.assertEqual(diff['1,020 inches'], '1,020 inches (25.91 m)')
        self.assertEqual(diff['10-12 ft'], '10-12 ft (3.05-3.66 m)')
        self.assertEqual(diff['10-12 in'], '10-12 in (25.40-30.48 cm)')
