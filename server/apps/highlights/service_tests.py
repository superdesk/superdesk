# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from test_factory import SuperdeskTestCase

from unittest import mock
from unittest.mock import MagicMock


class MarkedForHighlightsServiceTest(SuperdeskTestCase):
    """Base class for MarkedForHighlightsService tests."""

    def setUp(self):
        from apps.highlights import init_app
        super().setUp()
        # with self.app.app_context():
        init_app(self.app)

        try:
            from apps.highlights.service import MarkedForHighlightsService
        except ImportError:
            self.fail(
                "Could not import class under test "
                "(MarkedForHighlightsService).")
        else:
            self.instance = MarkedForHighlightsService()


@mock.patch('apps.highlights.service.push_notification')
@mock.patch('apps.highlights.service.get_resource_service')
class CreateMethodTestCase(MarkedForHighlightsServiceTest):
    """Tests for the create() method."""

    def setUp(self):
        super().setUp()

        db_item_1 = {
            '_id': 'tag:item_1',
            'highlights': [],
            '_updated': '01.01.1111',
            '_etag': '111',
        }
        db_item_2 = {
            '_id': 'tag:item_2',
            'highlights': [],
            '_updated': '02.02.2222',
            '_etag': '222',
        }

        # some of the existing archive items in database
        self.db_items = {
            'tag:item_1': db_item_1,
            'tag:item_2': db_item_2
        }

    def test_pushes_notifications_for_newly_highlighted_items(
        self, fake_get_service, fake_push_notify
    ):

        def fake_find_one(**kwargs):
            item_id = kwargs.get('guid')
            return self.db_items.get(item_id)

        fake_archive_service = MagicMock()
        fake_archive_service.find_one = fake_find_one

        fake_get_service.return_value = fake_archive_service

        # items' data in HTTP request
        req_item_1 = {
            'marked_item': 'tag:item_1',
            'highlights': 'highlight_X'
        }
        req_item_2 = {
            'marked_item': 'tag:item_2',
            'highlights': 'highlight_Y'
        }

        self.instance.create([req_item_1, req_item_2])

        # notifications should have been pushed, one for each highlighted item
        self.assertEqual(fake_push_notify.call_count, 2)
        fake_push_notify.assert_any_call(
            'item:highlight',
            marked=1,
            item_id='tag:item_1',
            highlight_id='highlight_X'
        )
        fake_push_notify.assert_any_call(
            'item:highlight',
            marked=1,
            item_id='tag:item_2',
            highlight_id='highlight_Y'
        )

    def test_pushes_notifications_for_newly_unhighlighted_items(
        self, fake_get_service, fake_push_notify
    ):
        # existing items ARE highlighted, and we will test toggling this off
        self.db_items['tag:item_1']['highlights'] = ['highlight_X']
        self.db_items['tag:item_2']['highlights'] = ['highlight_Y']

        def fake_find_one(**kwargs):
            item_id = kwargs.get('guid')
            return self.db_items.get(item_id)

        fake_archive_service = MagicMock()
        fake_archive_service.find_one = fake_find_one

        fake_get_service.return_value = fake_archive_service

        # items' data in HTTP request
        req_item_1 = {
            'marked_item': 'tag:item_1',
            'highlights': 'highlight_X'
        }
        req_item_2 = {
            'marked_item': 'tag:item_2',
            'highlights': 'highlight_Y'
        }

        self.instance.create([req_item_1, req_item_2])

        # notifications should have been pushed, one for each highlighted item
        self.assertEqual(fake_push_notify.call_count, 2)
        fake_push_notify.assert_any_call(
            'item:highlight',
            marked=0,
            item_id='tag:item_1',
            highlight_id='highlight_X'
        )
        fake_push_notify.assert_any_call(
            'item:highlight',
            marked=0,
            item_id='tag:item_2',
            highlight_id='highlight_Y'
        )
