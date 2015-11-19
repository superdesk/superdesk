# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from test_factory import SuperdeskTestCase
from superdesk import get_resource_service
from .broadcast import ARCHIVE_BROADCAST_NAME


class ArchiveBroadcastTestCase(SuperdeskTestCase):

    def setUp(self):
        super().setUp()
        self.service = get_resource_service(ARCHIVE_BROADCAST_NAME)

    def test_broadcast_content(self):
        content = {
            'genre': [{'name': 'Broadcast Script', 'value': 'Broadcast Script'}]
        }

        self.assertTrue(self.service.is_broadcast(content))

    def test_broadcast_content_if_genre_is_none(self):
        content = {
            'genre': None
        }

        self.assertFalse(self.service.is_broadcast(content))

    def test_broadcast_content_if_genre_is_empty_list(self):
        content = {
            'genre': []
        }

        self.assertFalse(self.service.is_broadcast(content))

    def test_broadcast_content_if_genre_is_other_than_broadcast(self):
        content = {
            'genre': [{'name': 'Article', 'value': 'Article'}]
        }

        self.assertFalse(self.service.is_broadcast(content))
