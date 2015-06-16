# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from apps.publish.publish_filters.filter_condition import FilterConditionService
from eve.utils import ParsedRequest
import json
import superdesk
import re


class FilterConditionTests(TestCase):

    def setUp(self):
        super().setUp()
        self.req = ParsedRequest()
        with self.app.app_context():
            self.app.data.insert('archive', [{'_id': '1', 'urgency': 1, 'headline': 'story', 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '2', 'headline': 'prtorque', 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '3', 'urgency': 3, 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '4', 'urgency': 4, 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '5', 'urgency': 2, 'state': 'fetched'}])
            self.app.data.insert('archive', [{'_id': '6', 'state': 'fetched'}])

    def _setup_elastic_args(self, elastic_translation, search_type='filter'):
        if search_type == 'keyword':
            self.req.args = {'source': json.dumps({'query': {'bool': {'should': [elastic_translation]}}})}
        elif search_type == 'not':
            self.req.args = {'source': json.dumps({'query': {'bool': {'must_not': [elastic_translation]}}})}
        elif search_type == 'filter':
            self.req.args = {'source': json.dumps({'query': {
                                                   'filtered': {
                                                       'filter': {
                                                           'bool': {
                                                               'should': [elastic_translation]}}}}})}

    def test_mongo_using_like_filter_complete_string(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'story'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEquals(1, docs.count())
            self.assertEquals('1', docs[0]['_id'])

    def test_mongo_using_like_filter_partial_string(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'tor'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEquals(2, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)

    def test_mongo_using_startswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'startswith', 'value': 'Sto'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEquals(1, docs.count())
            self.assertEquals('1', docs[0]['_id'])

    def test_mongo_using_endswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'endswith', 'value': 'Que'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEquals(1, docs.count())
            self.assertEquals('2', docs[0]['_id'])

    def test_mongo_using_notlike_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'notlike', 'value': 'Que'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEquals(5, docs.count())
            doc_ids = [d['_id'] for d in docs]
            self.assertTrue('2' not in doc_ids)

    def test_mongo_using_in_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'in', 'value': '3,4'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEquals(2, docs.count())
            self.assertEquals('3', docs[0]['_id'])
            self.assertEquals('4', docs[1]['_id'])

    def test_mongo_using_notin_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'nin', 'value': '2,3,4'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEquals(3, docs.count())
            doc_ids = [d['_id'] for d in docs]
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)

    def test_elastic_using_in_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'in', 'value': '3,4'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query)
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEquals(2, docs.count())
            self.assertTrue('4' in doc_ids)
            self.assertTrue('3' in doc_ids)

    def test_elastic_using_nin_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'nin', 'value': '3,4'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query, 'not')
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            self.assertEquals(4, docs.count())
            doc_ids = [d['_id'] for d in docs]
            self.assertTrue('6' in doc_ids)
            self.assertTrue('5' in doc_ids)

    def test_elastic_using_like_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'Tor'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query, 'keyword')
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            self.assertEquals(2, docs.count())
            doc_ids = [d['_id'] for d in docs]
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)

    def test_elastic_using_notlike_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'notlike', 'value': 'que'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query, 'not')
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            self.assertEquals(5, docs.count())
            doc_ids = [d['_id'] for d in docs]
            self.assertTrue('2' not in doc_ids)

    def test_elastic_using_startswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'startswith', 'value': 'Sto'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query, 'keyword')
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            self.assertEquals(1, docs.count())
            self.assertEquals('1', docs[0]['_id'])

    def test_elastic_using_endswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'endswith', 'value': 'Que'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query, 'keyword')
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            self.assertEquals(1, docs.count())
            self.assertEquals('2', docs[0]['_id'])

    def test_get_mongo_operator(self):
        f = FilterConditionService()
        self.assertEquals(f._get_mongo_operator('in'), '$in')
        self.assertEquals(f._get_mongo_operator('nin'), '$nin')
        self.assertEquals(f._get_mongo_operator('like'), '$regex')
        self.assertEquals(f._get_mongo_operator('notlike'), '$not')
        self.assertEquals(f._get_mongo_operator('startswith'), '$regex')
        self.assertEquals(f._get_mongo_operator('endswith'), '$regex')

    def test_get_mongo_value(self):
        f = FilterConditionService()
        self.assertEquals(f._get_mongo_value('in', '1,2'), [1, 2])
        self.assertEquals(f._get_mongo_value('nin', '3'), ['3'])
        self.assertEquals(f._get_mongo_value('like', 'test'), re.compile('.*test.*', re.IGNORECASE))
        self.assertEquals(f._get_mongo_value('notlike', 'test'), re.compile('.*test.*', re.IGNORECASE))
        self.assertEquals(f._get_mongo_value('startswith', 'test'), re.compile('^test', re.IGNORECASE))
        self.assertEquals(f._get_mongo_value('endswith', 'test'), re.compile('.*test', re.IGNORECASE))
