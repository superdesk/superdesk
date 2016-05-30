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
from .locator_mapper import LocatorMapper


class SelectorcodeMapperTest(SuperdeskTestCase):

    desks = [{'_id': 1, 'name': 'National'},
             {'_id': 2, 'name': 'Sports'},
             {'_id': 3, 'name': 'Finance'}]

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
    article5 = {
        'subject': [{'qcode': '15000000'}, {'qcode': '15063000'}]

    }
    category1 = 'I'
    category2 = 'D'
    locator_map = LocatorMapper()
    vocab = [{'_id': 'categories', 'items': [
        {"is_active": True, "name": "Overseas Sport", "qcode": "S", "subject": "15000000"},
        {"is_active": True, "name": "Domestic Sport", "qcode": "T", "subject": "15000000"},
        {'is_active': True, 'name': 'Finance', 'qcode': 'F', 'subject': '04000000'},
        {'is_active': True, 'name': 'World News', 'qcode': 'I'},
        {"is_active": True, "name": "Entertainment", "qcode": "e", "subject": "01000000"},
        {"is_active": True, "name": "Australian General News", "qcode": "a"}
    ]}]

    def setUp(self):
        super().setUp()
        self.app.data.insert('desks', self.desks)
        self.app.data.insert('vocabularies', self.vocab)
        init_app(self.app)

    def test_locator_code_for_international_domestic_news(self):
        self.assertEqual(self.locator_map.map(self.article1, self.category1), 'TRAVI')
        self.assertEqual(self.locator_map.map(self.article2, self.category2), 'TRAVD')

    def test_locator_code_for_international_domestic_sport(self):
        self.assertEqual(self.locator_map.map(self.article3, 'S'), 'VOL')
        self.assertEqual(self.locator_map.map(self.article3, 'T'), 'VOL')
        self.assertEqual(self.locator_map.map(self.article5, 'T'), 'TTEN')

    def test_locator_code_is_none(self):
        self.assertIsNone(self.locator_map.map(self.article4, self.category2))
