# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license*.


import os
import logging
from datetime import datetime
from superdesk.io.file_ingest_service import FileIngestService
from superdesk.utc import utc
from superdesk.utils import get_sorted_files, FileSortAttributes
from superdesk.errors import ParserError, ProviderError
from superdesk.io.iptc7901 import Iptc7901FileParser

logger = logging.getLogger(__name__)


class DPAIngestService(FileIngestService):

    PROVIDER = 'dpa'

    ERRORS = [ParserError.IPTC7901ParserError().get_error_description(),
              ProviderError.ingestError().get_error_description()]

    def __init__(self):
        self.parser = Iptc7901FileParser()

    def _update(self, provider):
        self.provider = provider
        self.path = provider.get('config', {}).get('path', None)

        if not self.path:
            logger.info('No path')
            return []

        for filename in get_sorted_files(self.path, sort_by=FileSortAttributes.created):
            try:
                filepath = os.path.join(self.path, filename)
                if os.path.isfile(filepath):
                    stat = os.lstat(filepath)
                    last_updated = datetime.fromtimestamp(stat.st_mtime, tz=utc)
                    if self.is_latest_content(last_updated, provider.get('last_updated')):
                        item = self.parser.parse_file(filepath)

                        self.move_file(self.path, filename, provider=provider, success=True)
                        yield [item]
                    else:
                        self.move_file(self.path, filename, provider=provider, success=True)
            except ParserError.IPTC7901ParserError() as ex:
                logger.exception("Ingest Type: DPA - File: {0} could not be processed".format(filename))
                self.move_file(self.path, filename, provider=provider, success=False)
                raise ParserError.IPTC7901ParserError(ex, provider)
            except ParserError as ex:
                self.move_file(self.path, filename, provider=provider, success=False)
            except Exception as ex:
                self.move_file(self.path, filename, provider=provider, success=False)
                raise ProviderError.ingestError(ex, provider)
