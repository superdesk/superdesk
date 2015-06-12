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
from apps.publish.blocking_filters.filter_condition import FilterConditionService
from eve.utils import ParsedRequest
import json
import superdesk


class FilterConditionTests(TestCase):

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('archive', [{'_id': '1', 'headline': 'story'}])
            self.app.data.insert('archive', [{'_id': '2', 'headline': 'prtorque'}])
            self.app.data.insert('archive', [{'_id': '3'}])
            self.app.data.insert('archive', [{'_id': '4'}])
            self.app.data.insert('archive', [{'_id': '5'}])
            self.app.data.insert('archive', [{'_id': '6'}])

    def get_expired_items(self, now):
        query_filter = self.get_query_for_expired_items(now)
        req = ParsedRequest()
        req.sort = '_created'
        req.max_results = 100
        return superdesk.get_resource_service('published').get_from_mongo(req=req, lookup=query_filter)

    def get_query_for_expired_items(self, now):
        query = {
            '$and': [
                {'expiry': {'$lte': now}},
                {'state': {'$ne': 'scheduled'}}
            ]
        }
        return query


    def test_using_like_filter_complete_string(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'story'}
        f.translate_to_mongo(doc)
        with self.app.app_context():
            req = ParsedRequest()
            docs = superdesk.get_resource_service('archive').get_from_mongo(req=req, lookup=doc['mongo_translation'])
            self.assertEquals(1, docs.count())
            self.assertEquals('1', docs[0]['_id'])

    def test_using_like_filter_partial_string(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'tor'}
        f.translate_to_mongo(doc)
        with self.app.app_context():
            req = ParsedRequest()
            docs = superdesk.get_resource_service('archive').get_from_mongo(req=req, lookup=doc['mongo_translation'])
            self.assertEquals(2, docs.count())
            self.assertEquals('1', docs[0]['_id'])
            self.assertEquals('2', docs[1]['_id'])

    def test_using_startswith_filter(self):
        f = FilterConditionService()
        doc = {'field': 'headline', 'operator': 'like', 'value': 'tor'}
        f.translate_to_mongo(doc)
        with self.app.app_context():
            req = ParsedRequest()
            docs = superdesk.get_resource_service('archive').get_from_mongo(req=req, lookup=doc['mongo_translation'])
            self.assertEquals(2, docs.count())
            self.assertEquals('1', docs[0]['_id'])
            self.assertEquals('2', docs[1]['_id'])

    def test_get_operator(self):
        f = FilterConditionService()
        self.assertEquals(f.get_operator('in'), '$in')
        self.assertEquals(f.get_operator('nin'), '$nin')
        self.assertEquals(f.get_operator('like'), '$regex')
        self.assertEquals(f.get_operator('notlike'), '$not')
        self.assertEquals(f.get_operator('startswith'), '$regex')
        self.assertEquals(f.get_operator('endswith'), '$regex')

    def test_get_value(self):
        f = FilterConditionService()
        self.assertEquals(f.get_value('in', '1,2'), [1,2])
        self.assertEquals(f.get_value('nin', '3'), ['3'])
        self.assertEquals(f.get_value('like', 'test'), '.*test.*')
        self.assertEquals(f.get_value('notlike', 'test'), '.*test.*')
        self.assertEquals(f.get_value('startswith', 'test'), '/^test/i')
        self.assertEquals(f.get_value('endswith', 'test'), '/.*test/i')