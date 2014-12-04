
import os
import logging

from datetime import datetime
from .newsml_1_2 import NewsMLOneParser
from superdesk.io.file_ingest_service import FileIngestService
from superdesk.utils import get_sorted_files, FileSortAttributes
from ..utc import utc
from ..etree import etree
from superdesk.notification import push_notification
from superdesk.io import register_provider


logger = logging.getLogger(__name__)
PROVIDER = 'afp'


class AFPIngestService(FileIngestService):
    """AFP Ingest Service"""

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
                            item = self.parser.parse_message(etree.fromstring(f.read()))

                            self.add_timestamps(item)
                            self.move_file(self.path, filename, success=True)
                            yield [item]
                    else:
                        self.move_file(self.path, filename, success=True)
            except Exception as err:
                logger.exception(err)
                self.move_file(self.path, filename, success=False)

        push_notification('ingest:update')


register_provider(PROVIDER, AFPIngestService())
