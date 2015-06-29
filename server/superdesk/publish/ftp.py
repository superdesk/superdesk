# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import ftplib
from superdesk.publish import register_transmitter
from io import BytesIO
from superdesk.publish.publish_service import PublishService, get_file_extension
from superdesk.errors import PublishFtpError
errors = [PublishFtpError.ftpError().get_error_description()]

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class FTPPublishService(PublishService):
    """FTP Publish Service."""

    def config_from_url(self, url):
        """Parse given url into ftp config. Used for tests.

        :param url: url in form `ftp://username:password@host:port/dir`
        """
        url_parts = urlparse(url)
        return {
            'username': url_parts.username,
            'password': url_parts.password,
            'host': url_parts.hostname,
            'path': url_parts.path.lstrip('/'),
        }

    def _transmit(self, queue_item, subscriber):
        config = queue_item.get('destination', {}).get('config', {})

        try:
            with ftplib.FTP(config.get('host')) as ftp:
                ftp.login(config.get('username'), config.get('password'))
                ftp.cwd(config.get('path', '').lstrip('/'))
                ftp.set_pasv(config.get('passive', False))

                filename = '{}.{}'.format(queue_item['item_id'].replace(':', '-'), get_file_extension(queue_item))
                b = BytesIO(bytes(queue_item['formatted_item'], 'UTF-8'))

                ftp.storbinary("STOR " + filename, b)
        except PublishFtpError:
            raise
        except Exception as ex:
            raise PublishFtpError.ftpError(ex, config)

register_transmitter('ftp', FTPPublishService(), errors)
