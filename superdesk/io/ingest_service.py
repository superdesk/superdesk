from superdesk.utc import utc
import logging
from superdesk import SuperdeskError

logger = logging.getLogger(__name__)


class IngestProviderClosedError(SuperdeskError):
    status_code = 500
    payload = {}


class IngestService():
    """Base ingest service class."""

    def get_items(self, guid):
        raise LookupError()

    def _update(self, provider):
        raise NotImplementedError()

    def update(self, provider):
        if provider.get('is_closed', False):
            raise IngestProviderClosedError(message='Ingest Provider %s is closed' % provider.get('name', ''))
        else:
            self._update(provider)

    def add_timestamps(self, item):
        """
        Adds _created, firstcreated, versioncreated and _updated timestamps
        :param item:
        :return:
        """

        item['firstcreated'] = utc.localize(item['firstcreated'])
        item['versioncreated'] = utc.localize(item['versioncreated'])
