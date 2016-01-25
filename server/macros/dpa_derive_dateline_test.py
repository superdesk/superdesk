# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from unittest import TestCase
from .dpa_derive_dateline import dpa_derive_dateline


class DPADeriveDatelineTests(TestCase):

    def simple_case_test(self):
        item = dict()
        item['body_html'] = 'Madrid (dpa) - Results and standings Spanish Primera Division\r\n(kick-off times in GMT):'
        dpa_derive_dateline(item)
        self.assertEqual(item['dateline']['located']['city'], 'Madrid')

    def text_before_test(self):
        item = dict()
        item['body_html'] = '\r\nComedian Morales running as outsider in Guatemala =\r\n        \r\n'
        item['body_html'] += 'Guatemala City (dpa) - Comedian Jimmy Morales has one major asset'
        dpa_derive_dateline(item)
        self.assertEqual(item['dateline']['located']['city'], 'Guatemala City')

    def know_city_test(self):
        item = dict()
        item['body_html'] = 'Dubbo (dpa) - Where on earth is that'
        dpa_derive_dateline(item)
        self.assertEqual(item['dateline']['located']['city'], 'Dubbo')
        self.assertEqual(item['dateline']['located']['country'], 'Australia')

    def no_match_test(self):
        item = dict()
        item['body_html'] = 'No dateline here'
        dpa_derive_dateline(item)
        self.assertNotIn('dateline', item)
