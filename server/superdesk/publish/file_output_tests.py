# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os

from superdesk.tests import TestCase
from superdesk.publish.file_output import FilePublishService
from superdesk.errors import PublishFileError


class FileOutputTest(TestCase):
    def setUp(self):
        super().setUp()
        self.fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)))
        self.subscribers = [{"_id": "1", "name": "Test", "can_send_takes_packages": False, "media_type": "media",
                             "is_active": True, "sequence_num_settings": {"max": 10, "min": 1},
                             "destinations": [{"name": "AAP IPNEWS", "delivery_type": "email", "format": "AAP IPNEWS",
                                               "config": {"file_path": self.fixtures}
                                               }]}]

    def test_file_write_binary(self):
        item = {'item_id': 'test_file_name',
                'item_version': 1,
                'formatted_item': b'I was here',
                'destination': {"name": "AAP IPNEWS", "delivery_type": "email", "format": "AAP IPNEWS",
                                "config": {"file_path": self.fixtures}}
                }
        service = FilePublishService()
        try:
            service._transmit(item, self.subscribers)
            self.assertTrue(True)
        finally:
            path = os.path.join(self.fixtures, 'test_file_name-1.txt')
            if os.path.isfile(path):
                os.remove(path)

    def test_file_write_string(self):
        item = {'item_id': 'test_file_name',
                'item_version': 1,
                'formatted_item': 'I was here',
                'destination': {"name": "AAP IPNEWS", "delivery_type": "email", "format": "AAP IPNEWS",
                                "config": {"file_path": self.fixtures}}
                }
        service = FilePublishService()
        try:
            service._transmit(item, self.subscribers)
            self.assertTrue(True)
        finally:
            path = os.path.join(self.fixtures, 'test_file_name-1.txt')
            if os.path.isfile(path):
                os.remove(path)

    def test_file_write_fail(self):
        self.fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__) + '/xyz'))
        item = {'item_id': 'test_file_name',
                'item_version': 1,
                'formatted_item': 'I was here',
                'destination': {"name": "AAP IPNEWS", "delivery_type": "email", "format": "AAP IPNEWS",
                                "config": {"file_path": self.fixtures}}
                }

        with self.app.app_context():
            service = FilePublishService()
            try:
                service._transmit(item, self.subscribers)
            except PublishFileError as ex:
                self.assertEqual(ex.message, 'File publish error')
                self.assertEqual(ex.code, 13000)
