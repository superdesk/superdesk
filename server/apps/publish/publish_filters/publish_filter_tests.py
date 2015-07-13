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
from apps.publish import SubscribersService
from eve.utils import ParsedRequest
import json
import os
import superdesk
from settings import URL_PREFIX
from apps.vocabularies.command import VocabulariesPopulateCommand


class PublishFilterTests(TestCase):

    def setUp(self):
        super().setUp()
        self.req = ParsedRequest()
        with self.app.test_request_context(URL_PREFIX):
            self.f = PublishFilterService(datasource='publish_filters', backend=superdesk.get_backend())
            self.s = SubscribersService(datasource='subscribers', backend=superdesk.get_backend())

            self.articles = [{'_id': '1', 'urgency': 1, 'headline': 'story', 'state': 'fetched'},
                             {'_id': '2', 'headline': 'prtorque', 'state': 'fetched'},
                             {'_id': '3', 'urgency': 3, 'headline': 'creator', 'state': 'fetched'},
                             {'_id': '4', 'urgency': 4, 'state': 'fetched'},
                             {'_id': '5', 'urgency': 2, 'state': 'fetched'},
                             {'_id': '6', 'state': 'fetched'}]
            self.app.data.insert('archive', self.articles)

            self.app.data.insert('filter_conditions',
                                 [{'_id': 1,
                                   'field': 'headline',
                                   'operator': 'like',
                                   'value': 'tor',
                                   'name': 'test-1'}])
            self.app.data.insert('filter_conditions',
                                 [{'_id': 2,
                                   'field': 'urgency',
                                   'operator': 'in',
                                   'value': '2',
                                   'name': 'test-2'}])
            self.app.data.insert('filter_conditions',
                                 [{'_id': 3,
                                   'field': 'headline',
                                   'operator': 'endswith',
                                   'value': 'tor',
                                   'name': 'test-3'}])
            self.app.data.insert('filter_conditions',
                                 [{'_id': 4,
                                   'field': 'urgency',
                                   'operator': 'in',
                                   'value': '2,3,4',
                                   'name': 'test-4'}])
            self.app.data.insert('filter_conditions',
                                 [{'_id': 5,
                                   'field': 'headline',
                                   'operator': 'startswith',
                                   'value': 'sto',
                                   'name': 'test-5'}])

            self.app.data.insert('publish_filters',
                                 [{"_id": 1,
                                   "publish_filter": [{"expression": {"fc": [1]}}],
                                   "name": "soccer-only"}])

            self.app.data.insert('publish_filters',
                                 [{"_id": 2,
                                   "publish_filter": [{"expression": {"fc": [4, 3]}}],
                                   "name": "soccer-only2"}])

            self.app.data.insert('publish_filters',
                                 [{"_id": 3,
                                   "publish_filter": [{"expression": {"pf": [1], "fc": [2]}}],
                                   "name": "soccer-only3"}])

            self.app.data.insert('publish_filters',
                                 [{"_id": 4,
                                   "publish_filter": [{"expression": {"fc": [3]}}, {"expression": {"fc": [5]}}],
                                   "name": "soccer-only4"}])

            self.app.data.insert('subscribers',
                                 [{"_id": 1,
                                   "publish_filter": {"filter_id": 3, "filter_type": "blocking"},
                                   "name": "sub1"}])
            self.app.data.insert('subscribers',
                                 [{"_id": 2,
                                   "publish_filter": {"filter_id": 1, "filter_type": "blocking"},
                                   "name": "sub1"}])

    def test_build_mongo_query_using_like_filter_single_fc(self):
        doc = {'publish_filter': [{"expression": {"fc": [1]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = self.f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(3, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('3' in doc_ids)

    def test_build_mongo_query_using_like_filter_single_pf(self):
        doc = {'publish_filter': [{"expression": {"pf": [1]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = self.f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(3, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('3' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_filter_condition(self):
        doc = {'publish_filter': [{"expression": {"fc": [1]}}, {"expression": {"fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = self.f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(4, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('5' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_pf(self):
        doc = {'publish_filter': [{"expression": {"pf": [1]}}, {"expression": {"fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = self.f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(4, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('5' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_filter_condition2(self):
        doc = {'publish_filter': [{"expression": {"fc": [3, 4]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = self.f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_pf2(self):
        doc = {'publish_filter': [{"expression": {"pf": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = self.f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_condition3(self):
        doc = {'publish_filter': [{"expression": {"fc": [3, 4]}}, {"expression": {"fc": [1, 2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = self.f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_pf3(self):
        doc = {'publish_filter': [{"expression": {"pf": [2]}}, {"expression": {"pf": [1], "fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = self.f.build_mongo_query(doc)
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_elastic_query_using_like_filter_single_filter_condition(self):
        doc = {'publish_filter': [{"expression": {"fc": [1]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(3, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('3' in doc_ids)

    def test_build_elastic_query_using_like_filter_single_publish_filter(self):
        doc = {'publish_filter': [{"expression": {"pf": [1]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(3, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('3' in doc_ids)

    def test_build_elastic_query_using_like_filter_multi_filter_condition(self):
        doc = {'publish_filter': [{"expression": {"fc": [1]}}, {"expression": {"fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(4, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('3' in doc_ids)
            self.assertTrue('5' in doc_ids)

    def test_build_mongo_query_using_like_filter_multi_publish_filter(self):
        doc = {'publish_filter': [{"expression": {"pf": [1]}}, {"expression": {"fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(4, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)
            self.assertTrue('3' in doc_ids)
            self.assertTrue('5' in doc_ids)

    def test_build_elastic_query_using_like_filter_multi_filter_condition2(self):
        doc = {'publish_filter': [{"expression": {"fc": [3, 4]}}, {"expression": {"fc": [1, 2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_elastic_query_using_like_filter_multi_publish_filter2(self):
        doc = {'publish_filter': [{"expression": {"fc": [4, 3]}},
                                  {"expression": {"pf": [1], "fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_elastic_query_using_like_filter_multi_publish_filter3(self):
        doc = {'publish_filter': [{"expression": {"pf": [2]}}, {"expression": {"pf": [1], "fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_elastic_query_using_like_filter_multi_publish_filter4(self):
        doc = {'publish_filter': [{"expression": {"pf": [2]}}, {"expression": {"pf": [3]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_build_elastic_query_using_like_filter_multi_publish_filter4(self):
        doc = {'publish_filter': [{"expression": {"pf": [4], "fc": [4]}}], 'name': 'pf-1'}
        with self.app.app_context():
            query = {'query': {'filtered': {'query': self.f._get_elastic_query(doc)}}}
            self.req.args = {'source': json.dumps(query)}
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('3' in doc_ids)

    def test_does_match_using_like_filter_single_fc(self):
        doc = {'publish_filter': [{"expression": {"fc": [1]}}], 'name': 'pf-1'}
        with self.app.app_context():
            self.assertTrue(self.f.does_match(doc, self.articles[0]))
            self.assertTrue(self.f.does_match(doc, self.articles[1]))
            self.assertTrue(self.f.does_match(doc, self.articles[2]))
            self.assertFalse(self.f.does_match(doc, self.articles[3]))
            self.assertFalse(self.f.does_match(doc, self.articles[4]))
            self.assertFalse(self.f.does_match(doc, self.articles[5]))

    def test_does_match_using_like_filter_single_pf(self):
        doc = {'publish_filter': [{"expression": {"pf": [1]}}], 'name': 'pf-1'}
        with self.app.app_context():
            self.assertTrue(self.f.does_match(doc, self.articles[0]))
            self.assertTrue(self.f.does_match(doc, self.articles[1]))
            self.assertTrue(self.f.does_match(doc, self.articles[2]))
            self.assertFalse(self.f.does_match(doc, self.articles[3]))
            self.assertFalse(self.f.does_match(doc, self.articles[4]))
            self.assertFalse(self.f.does_match(doc, self.articles[5]))

    def test_does_match_using_like_filter_multi_fc(self):
        doc = {'publish_filter': [{"expression": {"fc": [1]}}, {"expression": {"fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            self.assertTrue(self.f.does_match(doc, self.articles[0]))
            self.assertTrue(self.f.does_match(doc, self.articles[1]))
            self.assertTrue(self.f.does_match(doc, self.articles[2]))
            self.assertFalse(self.f.does_match(doc, self.articles[3]))
            self.assertTrue(self.f.does_match(doc, self.articles[4]))
            self.assertFalse(self.f.does_match(doc, self.articles[5]))

    def test_does_match_using_like_filter_multi_pf(self):
        doc = {'publish_filter': [{"expression": {"pf": [1]}}, {"expression": {"fc": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            self.assertTrue(self.f.does_match(doc, self.articles[0]))
            self.assertTrue(self.f.does_match(doc, self.articles[1]))
            self.assertTrue(self.f.does_match(doc, self.articles[2]))
            self.assertFalse(self.f.does_match(doc, self.articles[3]))
            self.assertTrue(self.f.does_match(doc, self.articles[4]))
            self.assertFalse(self.f.does_match(doc, self.articles[5]))

    def test_does_match_using_like_filter_multi_fc2(self):
        doc = {'publish_filter': [{"expression": {"fc": [3, 4]}}], 'name': 'pf-1'}
        with self.app.app_context():
            self.assertFalse(self.f.does_match(doc, self.articles[0]))
            self.assertFalse(self.f.does_match(doc, self.articles[1]))
            self.assertTrue(self.f.does_match(doc, self.articles[2]))
            self.assertFalse(self.f.does_match(doc, self.articles[3]))
            self.assertFalse(self.f.does_match(doc, self.articles[4]))
            self.assertFalse(self.f.does_match(doc, self.articles[5]))

    def test_does_match_using_like_filter_multi_pf2(self):
        doc = {'publish_filter': [{"expression": {"pf": [2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            self.assertFalse(self.f.does_match(doc, self.articles[0]))
            self.assertFalse(self.f.does_match(doc, self.articles[1]))
            self.assertTrue(self.f.does_match(doc, self.articles[2]))
            self.assertFalse(self.f.does_match(doc, self.articles[3]))
            self.assertFalse(self.f.does_match(doc, self.articles[4]))
            self.assertFalse(self.f.does_match(doc, self.articles[5]))

    def test_does_match_using_like_filter_multi_fc3(self):
        doc = {'publish_filter': [{"expression": {"fc": [3, 4]}}, {"expression": {"fc": [1, 2]}}], 'name': 'pf-1'}
        with self.app.app_context():
            self.assertFalse(self.f.does_match(doc, self.articles[0]))
            self.assertFalse(self.f.does_match(doc, self.articles[1]))
            self.assertTrue(self.f.does_match(doc, self.articles[2]))
            self.assertFalse(self.f.does_match(doc, self.articles[3]))
            self.assertFalse(self.f.does_match(doc, self.articles[4]))
            self.assertFalse(self.f.does_match(doc, self.articles[5]))

    def test_does_match_using_like_filter_multi_pf3(self):
        doc = {'publish_filter': [{"expression": {"pf": [4], "fc": [4]}}], 'name': 'pf-1'}
        with self.app.app_context():
            self.assertFalse(self.f.does_match(doc, self.articles[0]))
            self.assertFalse(self.f.does_match(doc, self.articles[1]))
            self.assertTrue(self.f.does_match(doc, self.articles[2]))
            self.assertFalse(self.f.does_match(doc, self.articles[3]))
            self.assertFalse(self.f.does_match(doc, self.articles[4]))
            self.assertFalse(self.f.does_match(doc, self.articles[5]))

    def test_if_pf_is_used(self):
        with self.app.app_context():
            self.assertTrue(self.f._get_publish_filters_by_publish_filter(1).count() == 1)
            self.assertTrue(self.f._get_publish_filters_by_publish_filter(4).count() == 0)

    def test_if_fc_is_used(self):
        with self.app.app_context():
            self.assertTrue(len(self.f._get_publish_filters_by_filter_condition(1)) == 2)
            self.assertTrue(len(self.f._get_publish_filters_by_filter_condition(3)) == 2)
            self.assertTrue(len(self.f._get_publish_filters_by_filter_condition(2)) == 1)

    def test_get_subscribers_by_filter_condition(self):
        filter_condition1 = {'field': 'urgency', 'operator': 'in', 'value': '2'}
        filter_condition2 = {'field': 'urgency', 'operator': 'in', 'value': '1'}
        filter_condition3 = {'field': 'headline', 'operator': 'like', 'value': 'tor'}
        filter_condition4 = {'field': 'urgency', 'operator': 'nin', 'value': '3'}

        with self.app.app_context():
            cmd = VocabulariesPopulateCommand()
            filename = os.path.join(os.path.abspath(
                os.path.dirname("apps/prepopulate/data_initialization/vocabularies.json")), "vocabularies.json")
            cmd.run(filename)
            self.assertTrue(len(self.s._get_subscribers_by_filter_condition(filter_condition1)) == 1)
            self.assertTrue(len(self.s._get_subscribers_by_filter_condition(filter_condition2)) == 0)
            self.assertTrue(len(self.s._get_subscribers_by_filter_condition(filter_condition3)) == 2)
            self.assertTrue(len(self.s._get_subscribers_by_filter_condition(filter_condition4)) == 1)
