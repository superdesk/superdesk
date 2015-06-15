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
            self.app.data.insert('archive', [{'_id': '3', 'urgency': 3, 'headline': 'creator', 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '4', 'urgency': 4, 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '5', 'urgency': 2, 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '6', 'state': 'fetched'}])
            self.app.data.insert('filter_condition',
                                 [{'_id': 1,
                                   'field': 'headline',
                                   'operator': 'like',
                                   'value': 'tor',
                                   'name': 'test-1'}])
            self.app.data.insert('filter_condition',
                                 [{'_id': 2,
                                   'field': 'urgency',
                                   'operator': 'in',
                                   'value': 2,
                                   'name': 'test-2'}])
            self.app.data.insert('filter_condition',
                                 [{'_id': 3,
                                   'field': 'headline',
                                   'operator': 'endswith',
                                   'value': 'tor',
                                   'name': 'test-3'}])
            self.app.data.insert('filter_condition',
                                 [{'_id': 4,
                                   'field': 'urgency',
                                   'operator': 'in',
                                   'value': '2,3,4',
                                   'name': 'test-4'}])

    def test_build_mongo_query_using_like_filter_single_condition(self):
        f = PublishFilterService()
        doc = {'publish_filter': [[1]], 'name': 'pf-1'}
        with self.app.app_context():
            query = f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [doc['_id'] for doc in docs]
            self.assertEquals(2, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_condition(self):
        f = PublishFilterService()
        doc = {'publish_filter': [[1], [2]], 'name': 'pf-1'}
        with self.app.app_context():
            query = f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [doc['_id'] for doc in docs]
            self.assertEquals(1, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('5' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_condition(self):
        f = PublishFilterService()
        doc = {'publish_filter': [[4, 3]], 'name': 'pf-1'}
        with self.app.app_context():
            query = f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [doc['_id'] for doc in docs]
            self.assertEquals(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_condition(self):
        f = PublishFilterService()
        doc = {'publish_filter': [[4, 3], [1, 2]], 'name': 'pf-1'}
        with self.app.app_context():
            query = f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [doc['_id'] for doc in docs]
            self.assertEquals(1, docs.count())
            self.assertTrue('3' in doc_ids)
