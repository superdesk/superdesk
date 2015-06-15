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
from apps.publish.publish_filters.publish_filter import PublishFilterService
from eve.utils import ParsedRequest
import json
import superdesk
import re


class PublishFilterTests(TestCase):

    def setUp(self):
        super().setUp()
        self.req = ParsedRequest()
        with self.app.app_context():
            self.app.data.insert('archive', [{'_id': '1', 'headline': 'story', 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '2', 'headline': 'prtorque', 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '3', 'urgency': 3, 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '4', 'urgency': 4, 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '5', 'urgency': 2, 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '6', 'state': 'fetched'}])

    def test_mongo_using_like_filter_complete_string(self):
        f = PublishFilterService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'story'}
        f._translate_to_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=doc['mongo_query'])
            self.assertEquals(1, docs.count())
            self.assertEquals('1', docs[0]['_id'])