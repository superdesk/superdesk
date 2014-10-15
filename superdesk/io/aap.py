
import os
import logging

from datetime import datetime
from .nitf import parse
from superdesk.utc import utc, timezone
from superdesk.notification import push_notification
from superdesk.io import register_provider, IngestService


logger = logging.getLogger(__name__)
PROVIDER = 'aap'


def normalize_date(naive, tz):
    return utc.normalize(tz.localize(naive))


class AAPIngestService(IngestService):
    """AAP Ingest Service"""

    def __init__(self):
        self.tz = timezone('Australia/Sydney')

    def prepare_href(self, href):
        return href

    def update(self, provider):
        self.provider = provider
        self.path = provider.get('config', {}).get('path', None)
        if not self.path:
            return

        for filename in os.listdir(self.path):
            try:
                if os.path.isfile(os.path.join(self.path, filename)):
                    filepath = os.path.join(self.path, filename)
                    stat = os.lstat(filepath)
                    last_updated = datetime.fromtimestamp(stat.st_mtime, tz=utc)
                    if self.is_latest_content(last_updated, provider.get('updated')):
                        with open(os.path.join(self.path, filename), 'r') as f:
                            item = parse(f.read())
                            item['firstcreated'] = normalize_date(item.get('firstcreated'), self.tz)
                            item['versioncreated'] = normalize_date(item.get('versioncreated'), self.tz)
                            item['created'] = item['firstcreated']
                            item['updated'] = item['versioncreated']
                            item.setdefault('provider', provider.get('name', provider['type']))
                            self.move_file(self.path, filename, success=True)
                            yield [item]
                    else:
                        self.move_file(self.path, filename, success=True)
            except (Exception) as err:
                logger.exception(err)
                self.move_file(self.path, filename, success=False)
                pass

        push_notification('ingest:update')

register_provider(PROVIDER, AAPIngestService())
