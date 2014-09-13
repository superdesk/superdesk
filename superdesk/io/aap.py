
import os
from datetime import datetime, timedelta

from .nitf import parse
from superdesk.utc import utc, utcnow, timezone
from superdesk.io import register_provider, IngestService

PROVIDER = 'aap'


def is_ready(last_updated, provider_last_updated=None):
    """Parse file only if it's not older than provider last update -10m"""

    if not provider_last_updated:
        provider_last_updated = utcnow() - timedelta(days=7)

    return provider_last_updated - timedelta(minutes=10) < last_updated


def normalize_date(naive, tz):
    return utc.normalize(tz.localize(naive))


class AAPIngestService(IngestService):
    """AAP Ingest Service"""

    def __init__(self):
        self.tz = timezone('Australia/Sydney')

    def prepare_href(self, href):
        return href

    def update(self, provider):
        path = provider.get('config', {}).get('path', None)
        if not path:
            return

        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            stat = os.lstat(filepath)
            last_updated = datetime.fromtimestamp(stat.st_mtime, tz=utc)
            if is_ready(last_updated, provider.get('updated')):
                with open(os.path.join(path, filename), 'r') as f:
                    item = parse(f.read())
                    item['firstcreated'] = normalize_date(item.get('firstcreated'), self.tz)
                    item['versioncreated'] = normalize_date(item.get('versioncreated'), self.tz)
                    item['created'] = item['firstcreated']
                    item['updated'] = item['versioncreated']
                    item.setdefault('provider', provider.get('name', provider['type']))
                    yield [item]

register_provider(PROVIDER, AAPIngestService())
