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
from .length_nautical_miles_to_metric import nautical_miles_to_metric


class MilesTestCase(unittest.TestCase):

    def test_m_to_km(self):
        text = 'Tom rides 125 nautical miles everyday. ' \
               'Tom rides 1 Nautical mile everyday. ' \
               'Tom rides 125 Nautical Miles everyday. ' \
               'Tom rides 125-nautical Miles everyday. ' \
               'Tom rides 12.5 nmi everyday. ' \
               'Tom rides 12.5nmi everyday. ' \
               'Tom rides 12.5-nmi everyday. ' \
               'Tom rides 12,500 nautical miles everyday. ' \
               'Tom rides 100-12500 Nautical Miles everyday. ' \

        item = {'body_html': text}
        res, diff = nautical_miles_to_metric(item)
        self.assertEqual(diff['125 nautical miles'], '125 nautical miles (231.5 km)')
        self.assertEqual(diff['1 Nautical mile'], '1 Nautical mile (1.9 km)')
        self.assertEqual(diff['125 Nautical Miles'], '125 Nautical Miles (231.5 km)')
        self.assertEqual(diff['125-nautical Miles'], '125-nautical Miles (231.5 km)')
        self.assertEqual(diff['12.5 nmi'], '12.5 nmi (23.2 km)')
        self.assertEqual(diff['12.5nmi'], '12.5nmi (23.2 km)')
        self.assertEqual(diff['12.5-nmi'], '12.5-nmi (23.2 km)')
        self.assertEqual(diff['12,500 nautical miles'], '12,500 nautical miles (23,150 km)')
        self.assertEqual(diff['100-12500 Nautical Miles'], '100-12500 Nautical Miles (185.2-23,150 km)')
