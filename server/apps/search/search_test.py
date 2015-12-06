# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE

from test_factory import SuperdeskTestCase
from eve.utils import ParsedRequest
from . import init_app


def resource_listener(resource, docs):
    for doc in docs['_items']:
        doc['_resource_listener'] = resource


def ingest_listener(docs):
    for doc in docs['_items']:
        doc['_ingest_listener'] = 1


class SearchServiceTestCase(SuperdeskTestCase):

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.app.data.insert('ingest', [{}])
            self.app.data.insert('archive', [{'_id': '456', 'task': {'desk': 1}, ITEM_STATE: CONTENT_STATE.PROGRESS},
                                             {'_id': '911', 'task': {'desk': None, 'user': 'test'},
                                              ITEM_STATE: CONTENT_STATE.PROGRESS},
                                             {'_id': '123', 'task': {'desk': 1}, ITEM_STATE: CONTENT_STATE.PUBLISHED},
                                             {'_id': '786', 'task': {'desk': 1}, ITEM_STATE: CONTENT_STATE.PUBLISHED}])
            self.app.data.insert('published', [{'item_id': '786', 'task': {'desk': 1},
                                                ITEM_STATE: CONTENT_STATE.PUBLISHED}])
            self.app.data.insert('archived', [{'item_id': '123', 'task': {'desk': 1},
                                               ITEM_STATE: CONTENT_STATE.PUBLISHED}])
            init_app(self.app)
            self.app.on_fetched_resource += resource_listener
            self.app.on_fetched_resource_ingest += ingest_listener

    def test_query_post_processing(self):
        with self.app.app_context():
            docs = self.app.data.find('search', None, None)
            self.assertEquals(4, docs.count())

            ingest_docs = [doc for doc in docs if doc['_type'] == 'ingest']
            self.assertEquals('ingest', ingest_docs[0]['_resource_listener'])
            self.assertEquals(1, ingest_docs[0]['_ingest_listener'])

            archive_docs = [doc for doc in docs if doc['_type'] == 'archive']
            self.assertNotIn('_ingest_listener', archive_docs[0])

    def test_using_repo_request_attribute(self):
        with self.app.app_context():
            req = ParsedRequest()
            req.args = {'repo': 'ingest'}
            docs = self.app.data.find('search', req, None)
            self.assertEquals(1, docs.count())
            self.assertEquals('ingest', docs[0]['_type'])

    def test_it_filters_out_private_content(self):
        with self.app.app_context():
            self.app.data.insert('archive', [{'task': {'desk': None}}, {'task': {}}])
            cursor = self.app.data.find('search', None, None)
            self.assertEquals(4, cursor.count())

    def test_it_includes_published_content(self):
        with self.app.app_context():
            cursor = self.app.data.find('search', None, None)
            self.assertEquals(4, cursor.count())

    def test_it_excludes_published_content(self):
        with self.app.app_context():
            req = ParsedRequest()
            req.args = {'repo': 'archive'}
            docs = self.app.data.find('search', req, None)
            self.assertEquals(1, docs.count())
