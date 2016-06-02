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
from .length_miles_to_metric import miles_to_metric


class MilesTestCase(unittest.TestCase):

    def test_m_to_km(self):
        text = 'Tom rides 125 miles everyday. ' \
               'Tom rides 1 mile everyday. ' \
               'Tom rides 125 Miles everyday. ' \
               'Tom rides 125-Miles everyday. ' \
               'Tom rides 12.5 mi everyday. ' \
               'Tom rides 12.5mi everyday. ' \
               'Tom rides 12.5-mi everyday. ' \
               'Tom rides 12,500 miles everyday. ' \
               'Tom rides 100-12500 Miles everyday. ' \

        item = {'body_html': text}
        res, diff = miles_to_metric(item)
        self.assertEqual(diff['125 miles'], '125 miles (201.2 km)')
        self.assertEqual(diff['1 mile'], '1 mile (1.6 km)')
        self.assertEqual(diff['125 Miles'], '125 Miles (201.2 km)')
        self.assertEqual(diff['125-Miles'], '125-Miles (201.2 km)')
        self.assertEqual(diff['12.5 mi'], '12.5 mi (20.1 km)')
        self.assertEqual(diff['12.5mi'], '12.5mi (20.1 km)')
        self.assertEqual(diff['12.5-mi'], '12.5-mi (20.1 km)')
        self.assertEqual(diff['12,500 miles'], '12,500 miles (20,117 km)')
        self.assertEqual(diff['100-12500 Miles'], '100-12500 Miles (160.9-20,117 km)')
