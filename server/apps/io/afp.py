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
import logging

from datetime import datetime
from superdesk.io.newsml_1_2 import NewsMLOneParser
from superdesk.io.file_ingest_service import FileIngestService
from superdesk.utils import get_sorted_files, FileSortAttributes
from superdesk.utc import utc
from superdesk.etree import etree, ParseError as etreeParserError
from superdesk.notification import push_notification
from superdesk.errors import ParserError, ProviderError


logger = logging.getLogger(__name__)


class AFPIngestService(FileIngestService):
    """AFP Ingest Service"""

    PROVIDER = 'afp'

    ERRORS = [ParserError.newsmlOneParserError().get_error_description(),
              ProviderError.ingestError().get_error_description()]

    def __init__(self):
        self.parser = NewsMLOneParser()

    def _update(self, provider):
        self.provider = provider
        self.path = provider.get('config', {}).get('path', None)
        if not self.path:
            return

        for filename in get_sorted_files(self.path, sort_by=FileSortAttributes.created):
            try:
                if os.path.isfile(os.path.join(self.path, filename)):
                    filepath = os.path.join(self.path, filename)
                    stat = os.lstat(filepath)
                    last_updated = datetime.fromtimestamp(stat.st_mtime, tz=utc)
                    if self.is_latest_content(last_updated, provider.get('last_updated')):
                        with open(os.path.join(self.path, filename), 'r') as f:
                            item = self.parser.parse_message(etree.fromstring(f.read()), provider)

                            self.add_timestamps(item)
                            self.move_file(self.path, filename, provider=provider, success=True)
                            yield [item]
                    else:
                        self.move_file(self.path, filename, provider=provider, success=True)
            except etreeParserError as ex:
                logger.exception("Ingest Type: AFP - File: {0} could not be processed".format(filename), ex)
                self.move_file(self.path, filename, provider=provider, success=False)
                raise ParserError.newsmlOneParserError(ex, provider)
            except ParserError as ex:
                self.move_file(self.path, filename, provider=provider, success=False)
            except Exception as ex:
                self.move_file(self.path, filename, provider=provider, success=False)
                raise ProviderError.ingestError(ex, provider)

        push_notification('ingest:update')
