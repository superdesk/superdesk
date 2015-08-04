# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from apps.publish import init_app
from apps.publish.formatters.field_mappers.locator_mapper import LocatorMapper


class SelectorcodeMapperTest(TestCase):

    desks = [{'_id': 1, 'name': 'National'},
             {'_id': 2, 'name': 'Sports'},
             {'_id': 3, 'name': 'Finance'}]

    def setUp(self):
        super().setUp()
        with self.app.app_context():
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
        self.assertEqual(f._map_subject_code(article1, category1, f.iptc_locators), 'TRAVI')
        self.assertEqual(f._map_subject_code(article2, category2, f.iptc_locators), 'TRAVD')
        self.assertEqual(f._map_subject_code(article3, category2, f.iptc_sports_locators), 'TTEN')
        self.assertIsNone(f._map_subject_code(article4, category2, f.iptc_sports_locators))
