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
import unittest
import ftplib

from superdesk.publish.ftp import FTPPublishService


class FTPPublishTestCase(unittest.TestCase):

    item = {'item_id': 'abc',
            'format': 'NITF',
            'formatted_item': '1234567890'}

    def is_item_loaded(self, url, uploaded_filename):
        config = FTPPublishService().config_from_url(url)
        with ftplib.FTP(config.get('host')) as ftp:
            ftp.login(config.get('username'), config.get('password'))
            ftp.cwd(config.get('path', ''))
            ftp.set_pasv(config.get('passive', False))

            for filename, facts in ftp.mlsd():
                if filename == uploaded_filename:
                    return True
            return False

    def test_it_can_connect(self):
        service = FTPPublishService()

        if 'FTP_URL' not in os.environ:
            return

        config = service.config_from_url(os.environ['FTP_URL'])
        self.item['destination'] = {'config': config}

        self.assertEqual('test', config['path'])
        self.assertEqual('localhost', config['host'])

        service._transmit(self.item, destination={'config': config})
        self.assertTrue(self.is_item_loaded(config, 'abc.ntf'))
