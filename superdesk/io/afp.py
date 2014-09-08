
import os
import shutil
import logging

from datetime import datetime, timedelta
from .newsml_1_2 import Parser
from ..utc import utc, utcnow, timezone
from ..etree import etree
from superdesk.notification import push_notification

logger = logging.getLogger(__name__)
PROVIDER = 'afp'


def is_ready(last_updated, provider_last_updated=None):
    """Parse file only if it's not older than provider last update -10m"""

    if not provider_last_updated:
        provider_last_updated = utcnow() - timedelta(days=7)

    return provider_last_updated - timedelta(minutes=10) < last_updated


def normalize_date(naive, tz):
    return utc.normalize(tz.localize(naive))


class AFPIngestService(object):
    """AFP Ingest Service"""

    def __init__(self):
        self.tz = timezone('Australia/Sydney')
        self.parser = Parser()

    def update(self, provider):
        self.provider = provider
        self.path = provider.get('config', {}).get('path', None)
        if not self.path:
            return

        try:
            for filename in os.listdir(self.path):
                if os.path.isfile(os.path.join(self.path, filename)):
                    filepath = os.path.join(self.path, filename)
                    stat = os.lstat(filepath)
                    last_updated = datetime.fromtimestamp(stat.st_mtime, tz=utc)
                    if is_ready(last_updated, provider.get('updated')):
                        with open(os.path.join(self.path, filename), 'r') as f:
                            item = Parser().parse_message(etree.fromstring(f.read()))
                            item['firstcreated'] = normalize_date(item.get('firstcreated'), self.tz)
                            item['versioncreated'] = normalize_date(item.get('versioncreated'), self.tz)
                            item['created'] = item['firstcreated']
                            item['updated'] = item['versioncreated']
                            item.setdefault('provider', provider.get('name', provider['type']))
                            self.move_the_current_file(filename, success=True)
                            yield [item]
        except (Exception) as err:
            logger.exception(err)
            self.move_the_current_file(filename, success=False)
            pass
        finally:
            push_notification('ingest:update')

    def move_the_current_file(self, filename, success=True):
        try:
            if not os.path.exists(os.path.join(self.path, "_PROCESSED/")):
                os.makedirs(os.path.join(self.path, "_PROCESSED/"))
            if not os.path.exists(os.path.join(self.path, "_ERROR/")):
                os.makedirs(os.path.join(self.path, "_ERROR/"))

            if success:
                shutil.copy2(os.path.join(self.path, filename), os.path.join(self.path, "_PROCESSED/"))
            else:
                shutil.copy2(os.path.join(self.path, filename), os.path.join(self.path, "_ERROR/"))
        finally:
            os.remove(os.path.join(self.path, filename))
