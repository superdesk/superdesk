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
import ftplib
import tempfile
from datetime import datetime
from superdesk.utc import utc
from superdesk.etree import etree
from superdesk.io import get_xml_parser
from .ingest_service import IngestService
from superdesk.errors import IngestFtpError

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class FTPService(IngestService):
    """FTP Ingest Service."""

    DATE_FORMAT = '%Y%m%d%H%M%S'
    FILE_SUFFIX = '.xml'

    PROVIDER = 'ftp'

    ERRORS = [IngestFtpError.ftpUnknownParserError().get_error_description(),
              IngestFtpError.ftpError().get_error_description()]

    def config_from_url(self, url):
        """Parse given url into ftp config.

        :param url: url in form `ftp://username:password@host:port/dir`
        """
        url_parts = urlparse(url)
        return {
            'username': url_parts.username,
            'password': url_parts.password,
            'host': url_parts.hostname,
            'path': url_parts.path.lstrip('/'),
        }

    def _update(self, provider):
        config = provider.get('config', {})
        last_updated = provider.get('last_updated')

        if 'dest_path' not in config:
            config['dest_path'] = tempfile.mkdtemp(prefix='superdesk_ingest_')

        items = []
        try:
            with ftplib.FTP(config.get('host')) as ftp:
                ftp.login(config.get('username'), config.get('password'))
                ftp.cwd(config.get('path', ''))
                ftp.set_pasv(config.get('passive', False))

                items = []
                for filename, facts in ftp.mlsd():
                    if facts.get('type', '') != 'file':
                        continue

                    if not filename.lower().endswith(self.FILE_SUFFIX):
                        continue

                    if last_updated:
                        item_last_updated = datetime.strptime(facts['modify'], self.DATE_FORMAT).replace(tzinfo=utc)
                        if item_last_updated < last_updated:
                            continue

                    dest = os.path.join(config['dest_path'], filename)

                    try:
                        with open(dest, 'xb') as f:
                            ftp.retrbinary('RETR %s' % filename, f.write)
                    except FileExistsError:
                        continue

                    xml = etree.parse(dest).getroot()
                    parser = get_xml_parser(xml)
                    if not parser:
                        raise IngestFtpError.ftpUnknownParserError(Exception('Parser not found'),
                                                                   provider, filename)
                    parsed = parser.parse_message(xml, provider)
                    if isinstance(parsed, dict):
                        parsed = [parsed]

                    items.append(parsed)
            return items
        except IngestFtpError:
            raise
        except Exception as ex:
            raise IngestFtpError.ftpError(ex, provider)
