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
from .temperature_fahrenheit_to_celsius import fahrenheit_to_celsius


class TemperatureTestCase(unittest.TestCase):

    def test_f_to_c(self):
        text = 'Todays temperature is 15.7 degrees Fahrenheit. ' \
               'Todays temperature is 15.7 Fahrenheit so it is hot. ' \
               'Todays temperature is 15.7 F so it is hot. ' \
               'Todays temperature is 15.7 °F so it is hot. ' \
               'Todays temperature is 15-17 °F so it is hot. ' \

        item = {'body_html': text}
        res, diff = fahrenheit_to_celsius(item)
        self.assertEqual(diff['15.7 degrees Fahrenheit'], '15.7 degrees Fahrenheit (-9.1 degrees Celsius)')
        self.assertEqual(diff['15.7 Fahrenheit'], '15.7 Fahrenheit (-9.1 degrees Celsius)')
        self.assertEqual(diff['15.7 F'], '15.7 F (-9.1 degrees Celsius)')
        self.assertEqual(diff['15.7 °F'], '15.7 °F (-9.1 degrees Celsius)')
        self.assertEqual(diff['15-17 °F'], '15-17 °F (-9.44--8.33 degrees Celsius)')
