# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from .rename_genre_value import rename_genre_value
from test_factory import SuperdeskTestCase


class RenameGenreTestCase(SuperdeskTestCase):
    articles = [{'guid': '1', '_id': '1', 'type': 'text',
                 'genre': [{'value': 'a', 'name': 'a'}]},
                {'guid': '2', '_id': '2', 'type': 'text',
                 'genre': [{'value': 'b', 'name': 'b'}, {'value': 'c', 'name': 'c'}]}]

    def setUp(self):
        super().setUp()
        self.app.data.insert('archive', self.articles)

    def test_rename_genre(self):
        kwargs = {'repo': 'archive'}
        rename_genre_value(**kwargs)
        archive_items = self.app.data.find_all('archive', None)
        for item in archive_items:
            if item['_id'] == '1':
                self.assertDictEqual(item['genre'][0], {'qcode': 'a', 'name': 'a'})
            if item['_id'] == 2:
                self.assertListEqual(item['genre'], [{'qcode': 'b', 'name': 'b'}, {'qcode': 'c', 'name': 'c'}])
