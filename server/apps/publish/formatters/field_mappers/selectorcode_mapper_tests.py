# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from test_factory import SuperdeskTestCase
from apps.publish import init_app
from apps.publish.formatters.field_mappers.selectorcode_mapper import SelectorcodeMapper


class SelectorcodeMapperTest(SuperdeskTestCase):

    desks = [{'_id': 1, 'name': 'National'},
             {'_id': 2, 'name': 'Sport'},
             {'_id': 3, 'name': 'Finance'}]

    def setUp(self):
        super().setUp()
        self.app.data.insert('desks', self.desks)
        init_app(self.app)

    def test_is_in_subject(self):
        article = {
            'subject': [{'qcode': '04001005'}, {'qcode': '15011002'}],
        }
        f = SelectorcodeMapper()
        self.assertTrue(f._is_in_subject(article, '150'))
        self.assertFalse(f._is_in_subject(article, '151'))
        self.assertTrue(f._is_in_subject(article, '04001'))

    def test_join_selector_codes(self):
        f = SelectorcodeMapper()
        result = f._join_selector_codes('ipnewS', 'newsi', 'cnewsi', 'cnewsi')
        result_list = result.split()
        self.assertEqual(len(result_list), 12)

    def test_set_selector_codes(self):
        article = {
            'task': {'desk': 1},
            'slugline': 'Test',
            'urgency': 3
        }
        subscriber = {'name': 'ipnews'}
        f = SelectorcodeMapper()
        odbc_item = {}
        with self.app.app_context():
            f.map(article, 'A', subscriber=subscriber, formatted_item=odbc_item)
            self.assertSetEqual(set(odbc_item['selector_codes'].split()),
                                set('and axd pnd cxd 0fh 0ir 0px 0ah 0hw cxx axx cnd 0nl az pxd pxx'.split()))
