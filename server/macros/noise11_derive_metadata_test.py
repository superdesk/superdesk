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
import datetime
from .noise11_derive_metadata import noise11_derive_metadata


class Noise11DeriveMetaDataTests(SuperdeskTestCase):

    vocab = [{'_id': 'categories', 'items': [{'is_active': True, 'name': 'Entertainment', 'qcode': 'e'}]}]
    now = datetime.datetime(2015, 6, 13, 11, 45, 19, 0)

    def setUp(self):
        super().setUp()
        self.app.data.insert('vocabularies', self.vocab)

    def simple_case_test(self):
        item = dict()
        item['firstcreated'] = datetime.datetime(2015, 10, 26, 11, 45, 19, 0)
        item['source'] = 'NOISE11'
        noise11_derive_metadata(item)
        self.assertEqual(item['dateline']['text'], 'SYDNEY Oct 26 NOISE11 -')
