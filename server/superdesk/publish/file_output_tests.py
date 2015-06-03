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
from apps.archive import init_app


class FileOutputTest(TestCase):
    def setUp(self):
        super().setUp()
        with self.app.app_context():
            init_app(self.app)

    def test_file_write(self):
        fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)))

        output_channel = {'config': {'file_path': fixtures}}

        item = {'item_id': 'test_file_name',
                'item_version': 1,
                'formatted_item': b'I was here'
                }
        service = FilePublishService()
        try:
            service._transmit(item, {}, output_channel)
            self.assertTrue(True)
        finally:
            path = os.path.join(fixtures, 'test_file_name-1.txt')
            if os.path.isfile(path):
                os.remove(path)

    def test_file_write_fail(self):
        with self.app.app_context():
            fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)))

            output_channel = {'config': {'file_path': fixtures}}

            item = {'item_id': 'test_file_name',
                    'item_version': 1,
                    'formatted_item': 'I was here'
                    }
            service = FilePublishService()
            try:
                service._transmit(item, {}, output_channel)
            except PublishFileError as ex:
                self.assertEqual(ex.message, 'File publish error')
                self.assertEqual(ex.code, 13000)
