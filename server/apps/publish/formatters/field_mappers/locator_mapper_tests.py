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
from apps.publish.formatters.field_mappers.locator_mapper import LocatorMapper


class SelectorcodeMapperTest(SuperdeskTestCase):

    desks = [{'_id': 1, 'name': 'National'},
             {'_id': 2, 'name': 'Sports'},
             {'_id': 3, 'name': 'Finance'}]

    def setUp(self):
        super().setUp()
        self.app.data.insert('desks', self.desks)
        init_app(self.app)

    def test_map_subject_code(self):
        article1 = {
            'subject': [{'qcode': '10006000'}, {'qcode': '15011002'}]

        }
        article2 = {
            'subject': [{'qcode': '15011002'}, {'qcode': '10006000'}]

        }
        article3 = {
            'subject': [{'qcode': '15063000'}, {'qcode': '15067000'}]

        }
        article4 = {
            'subject': [{'qcode': '9999999'}]

        }
        category1 = 'I'
        category2 = 'D'
        f = LocatorMapper()
        self.assertEqual(f.map(article1, category1), 'TRAVI')
        self.assertEqual(f.map(article2, category2), 'TRAVD')
        self.assertEqual(f.map(article3, 'S'), 'TTEN')
        self.assertIsNone(f.map(article4, category2))
