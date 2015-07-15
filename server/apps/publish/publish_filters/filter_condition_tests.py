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
import os
from settings import URL_PREFIX
from apps.vocabularies.command import VocabulariesPopulateCommand


class FilterConditionTests(TestCase):

    def setUp(self):
        super().setUp()
        self.req = ParsedRequest()
        with self.app.test_request_context(URL_PREFIX):
            self.articles = [{'_id': '1', 'urgency': 1, 'headline': 'story', 'state': 'fetched'},
                             {'_id': '2', 'headline': 'prtorque', 'state': 'fetched'},
                             {'_id': '3', 'urgency': 3, 'state': 'fetched'},
                             {'_id': '4', 'urgency': 4, 'state': 'fetched'},
                             {'_id': '5', 'urgency': 2, 'state': 'fetched'},
                             {'_id': '6', 'state': 'fetched'},
                             {'_id': '7', 'genre': [{'name': 'Sidebar'}], 'state': 'fetched'},
                             {'_id': '8', 'subject': [{'name': 'adult education',
                                                       'qcode': '05001000',
                                                       'parent': '05000000'},
                                                      {'name': 'high schools',
                                                       'qcode': '05005003',
                                                       'parent': '05005000'}], 'state': 'fetched'}]

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
                                   'field': 'urgency',
                                   'operator': 'in',
                                   'value': '3,4,5',
                                   'name': 'test-2'}])
            self.app.data.insert('filter_conditions',
                                 [{'_id': 4,
                                   'field': 'urgency',
                                   'operator': 'nin',
                                   'value': '1,2,3',
                                   'name': 'test-2'}])
            self.app.data.insert('filter_conditions',
                                 [{'_id': 5,
                                   'field': 'urgency',
                                   'operator': 'in',
                                   'value': '2,5',
                                   'name': 'test-2'}])
            self.app.data.insert('publish_filters',
                                 [{"_id": 1,
                                   "publish_filter": [{"expression": {"fc": [1]}}],
                                   "name": "soccer-only"}])

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

    def test_mongo_using_genre_filter_complete_string(self):
        f = FilterConditionService()
        doc = {'field': 'genre', 'operator': 'in', 'value': 'Sidebar'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEqual(1, docs.count())
            self.assertEqual('7', docs[0]['_id'])

    def test_mongo_using_subject_filter_complete_string(self):
        f = FilterConditionService()
        doc = {'field': 'subject', 'operator': 'in', 'value': '05005003'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEqual(1, docs.count())
            self.assertEqual('8', docs[0]['_id'])

    def test_mongo_using_like_filter_complete_string(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'story'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEqual(1, docs.count())
            self.assertEqual('1', docs[0]['_id'])

    def test_mongo_using_like_filter_partial_string(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'tor'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(2, docs.count())
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)

    def test_mongo_using_startswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'startswith', 'value': 'Sto'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEqual(1, docs.count())
            self.assertEqual('1', docs[0]['_id'])

    def test_mongo_using_endswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'endswith', 'value': 'Que'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEqual(1, docs.count())
            self.assertEqual('2', docs[0]['_id'])

    def test_mongo_using_notlike_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'notlike', 'value': 'Que'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEqual(7, docs.count())
            doc_ids = [d['_id'] for d in docs]
            self.assertTrue('2' not in doc_ids)

    def test_mongo_using_in_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'in', 'value': '3,4'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEqual(2, docs.count())
            self.assertEqual('3', docs[0]['_id'])
            self.assertEqual('4', docs[1]['_id'])

    def test_mongo_using_notin_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'nin', 'value': '2,3,4'}
        query = f.get_mongo_query(doc)
        with self.app.app_context():
            docs = superdesk.get_resource_service('archive').\
                get_from_mongo(req=self.req, lookup=query)
            self.assertEqual(5, docs.count())
            doc_ids = [d['_id'] for d in docs]
            self.assertTrue('1' in doc_ids)
            self.assertTrue('2' in doc_ids)

    def test_elastic_using_genre_filter_complete_string(self):
        f = FilterConditionService()
        doc = {'field': 'genre', 'operator': 'in', 'value': 'Sidebar'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query)
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('7' in doc_ids)

    def test_elastic_using_subject_filter_complete_string(self):
        f = FilterConditionService()
        doc = {'field': 'subject', 'operator': 'in', 'value': '05005003'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query)
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(1, docs.count())
            self.assertTrue('8' in doc_ids)

    def test_elastic_using_in_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'in', 'value': '3,4'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query)
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            doc_ids = [d['_id'] for d in docs]
            self.assertEqual(2, docs.count())
            self.assertTrue('4' in doc_ids)
            self.assertTrue('3' in doc_ids)

    def test_elastic_using_nin_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'nin', 'value': '3,4'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query, 'not')
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            self.assertEqual(6, docs.count())
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
            self.assertEqual(2, docs.count())
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
            self.assertEqual(7, docs.count())
            doc_ids = [d['_id'] for d in docs]
            self.assertTrue('2' not in doc_ids)

    def test_elastic_using_startswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'startswith', 'value': 'Sto'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query, 'keyword')
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            self.assertEqual(1, docs.count())
            self.assertEqual('1', docs[0]['_id'])

    def test_elastic_using_endswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'endswith', 'value': 'Que'}
        query = f.get_elastic_query(doc)
        with self.app.app_context():
            self._setup_elastic_args(query, 'keyword')
            docs = superdesk.get_resource_service('archive').get(req=self.req, lookup=None)
            self.assertEqual(1, docs.count())
            self.assertEqual('2', docs[0]['_id'])

    def test_get_mongo_operator(self):
        f = FilterConditionService()
        self.assertEqual(f._get_mongo_operator('in'), '$in')
        self.assertEqual(f._get_mongo_operator('nin'), '$nin')
        self.assertEqual(f._get_mongo_operator('like'), '$regex')
        self.assertEqual(f._get_mongo_operator('notlike'), '$not')
        self.assertEqual(f._get_mongo_operator('startswith'), '$regex')
        self.assertEqual(f._get_mongo_operator('endswith'), '$regex')

    def test_get_mongo_value(self):
        f = FilterConditionService()
        self.assertEqual(f._get_mongo_value('in', '1,2', 'urgency'), [1, 2])
        self.assertEqual(f._get_mongo_value('nin', '3', 'priority'), ['3'])
        self.assertEqual(f._get_mongo_value('like', 'test', 'headline'), re.compile('.*test.*', re.IGNORECASE))
        self.assertEqual(f._get_mongo_value('notlike', 'test', 'headline'), re.compile('.*test.*', re.IGNORECASE))
        self.assertEqual(f._get_mongo_value('startswith', 'test', 'headline'), re.compile('^test', re.IGNORECASE))
        self.assertEqual(f._get_mongo_value('endswith', 'test', 'headline'), re.compile('.*test', re.IGNORECASE))

    def test_does_match_with_like_full(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'story'}
        self.assertTrue(f.does_match(doc, self.articles[0]))
        self.assertFalse(f.does_match(doc, self.articles[1]))
        self.assertFalse(f.does_match(doc, self.articles[2]))
        self.assertFalse(f.does_match(doc, self.articles[3]))
        self.assertFalse(f.does_match(doc, self.articles[4]))
        self.assertFalse(f.does_match(doc, self.articles[5]))

    def test_does_match_with_like_partial(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'tor'}
        self.assertTrue(f.does_match(doc, self.articles[0]))
        self.assertTrue(f.does_match(doc, self.articles[1]))
        self.assertFalse(f.does_match(doc, self.articles[2]))
        self.assertFalse(f.does_match(doc, self.articles[3]))
        self.assertFalse(f.does_match(doc, self.articles[4]))
        self.assertFalse(f.does_match(doc, self.articles[5]))

    def test_does_match_with_startswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'startswith', 'value': 'Sto'}
        self.assertTrue(f.does_match(doc, self.articles[0]))
        self.assertFalse(f.does_match(doc, self.articles[1]))
        self.assertFalse(f.does_match(doc, self.articles[2]))
        self.assertFalse(f.does_match(doc, self.articles[3]))
        self.assertFalse(f.does_match(doc, self.articles[4]))
        self.assertFalse(f.does_match(doc, self.articles[5]))

    def test_does_match_with_endswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'endswith', 'value': 'Que'}
        self.assertFalse(f.does_match(doc, self.articles[0]))
        self.assertTrue(f.does_match(doc, self.articles[1]))
        self.assertFalse(f.does_match(doc, self.articles[2]))
        self.assertFalse(f.does_match(doc, self.articles[3]))
        self.assertFalse(f.does_match(doc, self.articles[4]))
        self.assertFalse(f.does_match(doc, self.articles[5]))

    def test_does_match_with_notlike_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'notlike', 'value': 'Que'}
        self.assertTrue(f.does_match(doc, self.articles[0]))
        self.assertFalse(f.does_match(doc, self.articles[1]))
        self.assertTrue(f.does_match(doc, self.articles[2]))
        self.assertTrue(f.does_match(doc, self.articles[3]))
        self.assertTrue(f.does_match(doc, self.articles[4]))
        self.assertTrue(f.does_match(doc, self.articles[5]))

    def test_does_match_with_genre_filter(self):
        f = FilterConditionService()
        doc = {'field': 'genre', 'operator': 'in', 'value': 'Sidebar'}
        self.assertFalse(f.does_match(doc, self.articles[0]))
        self.assertFalse(f.does_match(doc, self.articles[1]))
        self.assertFalse(f.does_match(doc, self.articles[2]))
        self.assertFalse(f.does_match(doc, self.articles[3]))
        self.assertFalse(f.does_match(doc, self.articles[4]))
        self.assertFalse(f.does_match(doc, self.articles[5]))
        self.assertTrue(f.does_match(doc, self.articles[6]))
        self.assertFalse(f.does_match(doc, self.articles[7]))

    def test_does_match_with_subject_filter(self):
        f = FilterConditionService()
        doc = {'field': 'subject', 'operator': 'in', 'value': '05005003'}
        self.assertFalse(f.does_match(doc, self.articles[0]))
        self.assertFalse(f.does_match(doc, self.articles[1]))
        self.assertFalse(f.does_match(doc, self.articles[2]))
        self.assertFalse(f.does_match(doc, self.articles[3]))
        self.assertFalse(f.does_match(doc, self.articles[4]))
        self.assertFalse(f.does_match(doc, self.articles[5]))
        self.assertFalse(f.does_match(doc, self.articles[6]))
        self.assertTrue(f.does_match(doc, self.articles[7]))

    def test_does_match_with_in_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'in', 'value': '3,4'}
        self.assertFalse(f.does_match(doc, self.articles[0]))
        self.assertFalse(f.does_match(doc, self.articles[1]))
        self.assertTrue(f.does_match(doc, self.articles[2]))
        self.assertTrue(f.does_match(doc, self.articles[3]))
        self.assertFalse(f.does_match(doc, self.articles[4]))
        self.assertFalse(f.does_match(doc, self.articles[5]))

    def test_does_match_with_nin_filter(self):
        f = FilterConditionService()
        doc = {'field': 'urgency', 'operator': 'nin', 'value': '2,3,4'}
        self.assertTrue(f.does_match(doc, self.articles[0]))
        self.assertTrue(f.does_match(doc, self.articles[1]))
        self.assertFalse(f.does_match(doc, self.articles[2]))
        self.assertFalse(f.does_match(doc, self.articles[3]))
        self.assertFalse(f.does_match(doc, self.articles[4]))
        self.assertTrue(f.does_match(doc, self.articles[5]))

    def test_are_equal1(self):
        f = FilterConditionService()
        new_doc = {'name': 'A', 'field': 'urgency', 'operator': 'nin', 'value': '2,3,4'}
        doc = {'_id': 1, 'name': 'B', 'field': 'urgency', 'operator': 'nin', 'value': '2,3,4'}
        self.assertTrue(f._are_equal(new_doc, doc))

    def test_are_equal2(self):
        f = FilterConditionService()
        new_doc = {'name': 'A', 'field': 'urgency', 'operator': 'nin', 'value': '4,2,3'}
        doc = {'_id': 1, 'name': 'B', 'field': 'urgency', 'operator': 'nin', 'value': '2,3,4'}
        self.assertTrue(f._are_equal(new_doc, doc))

    def test_are_equal3(self):
        f = FilterConditionService()
        new_doc = {'name': 'A', 'field': 'urgency', 'operator': 'nin', 'value': 'jump,track'}
        doc = {'_id': 1, 'name': 'B', 'field': 'urgency', 'operator': 'nin', 'value': 'tump,jrack'}
        self.assertTrue(f._are_equal(new_doc, doc))

    def test_are_equal4(self):
        f = FilterConditionService()
        new_doc = {'name': 'A', 'field': 'urgency', 'operator': 'nin', 'value': '4,2,3'}
        doc = {'_id': 1, 'name': 'B', 'field': 'urgency', 'operator': 'nin', 'value': '2,3'}
        self.assertFalse(f._are_equal(new_doc, doc))

    def test_if_fc_is_used(self):
        f = FilterConditionService()
        with self.app.app_context():
            self.assertTrue(f._get_referenced_filter_conditions(1).count() == 1)
            self.assertTrue(f._get_referenced_filter_conditions(2).count() == 0)

    def test_check_similar(self):
        f = superdesk.get_resource_service('filter_conditions')
        filter_condition1 = {'field': 'urgency', 'operator': 'in', 'value': '2'}
        filter_condition2 = {'field': 'urgency', 'operator': 'in', 'value': '3'}
        filter_condition3 = {'field': 'urgency', 'operator': 'in', 'value': '1'}
        filter_condition4 = {'field': 'urgency', 'operator': 'in', 'value': '5'}
        filter_condition5 = {'field': 'urgency', 'operator': 'nin', 'value': '5'}
        filter_condition6 = {'field': 'headline', 'operator': 'like', 'value': 'tor'}
        with self.app.app_context():
            cmd = VocabulariesPopulateCommand()
            filename = os.path.join(os.path.abspath(
                os.path.dirname("apps/prepopulate/data_initialization/vocabularies.json")), "vocabularies.json")
            cmd.run(filename)
            self.assertTrue(len(f._check_similar(filter_condition1)) == 2)
            self.assertTrue(len(f._check_similar(filter_condition2)) == 1)
            self.assertTrue(len(f._check_similar(filter_condition3)) == 0)
            self.assertTrue(len(f._check_similar(filter_condition4)) == 3)
            self.assertTrue(len(f._check_similar(filter_condition5)) == 1)
            self.assertTrue(len(f._check_similar(filter_condition6)) == 1)
