# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015, 2016 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from test_factory import SuperdeskTestCase
from ntb.scanpix.scanpix_datalayer import extract_params, extract_date


class ScanpixDatalayer(SuperdeskTestCase):

    def test_validate_query_all_first_succeeds(self):
        query = 'all headline:(head one) caption:(capt) keywords:(key) bw:(1) clear_edge:(1)'
        names = ['headline', 'caption', 'keywords', 'starred', 'bw', 'clear_edge']
        result = extract_params(query, names)
        self.assertDictEqual(result, {'q': 'all', 'headline': 'head one', 'caption': 'capt',
                                      'keywords': 'key', 'bw': '1', 'clear_edge': '1'},
                             msg='Fail to parse text query all first')

    def test_validate_query_all_middle_succeeds(self):
        query = 'headline:(head one) all caption:(capt)'
        names = ['headline']
        result = extract_params(query, names)
        self.assertDictEqual(result, {'q': 'all', 'headline': 'head one'},
                             msg='Fail to parse text query all middle')

    def test_validate_query_all_end_succeeds(self):
        query = 'headline:(head one) caption:(capt) all'
        names = ['headline']
        result = extract_params(query, names)
        self.assertDictEqual(result, {'q': 'all', 'headline': 'head one'},
                             msg='Fail to parse text query all end')

    def test_date_param_format_is_correct(self):
        date = '29/02/2016'
        self.assertEqual('29-02-2016', extract_date(date))
