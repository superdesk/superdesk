# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from .clean_keywords import clean_keywords
from test_factory import SuperdeskTestCase


class CleanKeywordsTestCase(SuperdeskTestCase):

    articles = [{'guid': 'aapimage-1', '_id': '1', 'type': 'text',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing']},
                {'guid': 'aapimage-2', '_id': '2', 'type': 'text',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing']},
                {'guid': 'aapimage-3', '_id': '3', 'type': 'text',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing']},
                {'guid': 'aapimage-4', '_id': '4', 'type': 'text',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing']},
                {'guid': 'aapimage-5', '_id': '5', 'type': 'text',
                 'keywords': ['Student', 'Crime', 'Police', 'Missing']},
                {'guid': '6', '_id': '6', 'type': 'text', 'keywords': ['Student', 'Crime', 'Police', 'Missing']},
                {'guid': '7', '_id': '7', 'type': 'text', 'keywords': ['Student', 'Crime', 'Police', 'Missing']},
                {'guid': '8', '_id': '8', 'type': 'text', 'keywords': ['Student', 'Crime', 'Police', 'Missing']}]

    def setUp(self):
        super().setUp()
        self.app.data.insert('archive', self.articles)

    def test_clear_keywords(self):
        kwargs = {'repo': 'archive'}
        clean_keywords(**kwargs)
        archive_items = self.app.data.find_all('archive', None)
        for item in archive_items:
            if item['guid'].find('aapimage') >= 0:
                self.assertEqual(item['keywords'], [])
            else:
                self.assertEqual(item['keywords'], ['Student', 'Crime', 'Police', 'Missing'])
