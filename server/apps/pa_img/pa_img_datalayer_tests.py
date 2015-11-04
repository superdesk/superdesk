# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from test_factory import SuperdeskTestCase
from apps.pa_img.pa_img_datalayer import extract_params


class PaImgDatalayer(SuperdeskTestCase):

    def test_validate_query_all_first_succeeds(self):
        query = '(all) headline:(head one) caption:(capt) keywords:(key)'
        names = ['headline', 'keywords']
        result = extract_params(query, names)
        self.assertDictEqual(result, {'text': 'all', 'headline': 'head one', 'keywords': 'key'},
                             msg='Fail to parse text query all first')

    def test_validate_query_all_middle_succeeds(self):
        query = 'headline:(head one) (all) caption:(capt) keywords:(key)'
        names = ['headline', 'keywords']
        result = extract_params(query, names)
        self.assertDictEqual(result, {'text': 'all', 'headline': 'head one', 'keywords': 'key'},
                             msg='Fail to parse text query all middle')

    def test_validate_query_all_end_succeeds(self):
        query = 'headline:(head one) caption:(capt) keywords:(key) (all)'
        names = ['headline', 'keywords']
        result = extract_params(query, names)
        self.assertDictEqual(result, {'text': 'all', 'headline': 'head one', 'keywords': 'key'},
                             msg='Fail to parse text query all end')
