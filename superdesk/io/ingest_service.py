from superdesk.utc import utc
import logging

logger = logging.getLogger(__name__)


class IngestService():
    """Base ingest service class."""

    def get_items(self, guid):
        raise LookupError()

    def update(self, provider):
        NotImplementedError()

    def add_timestamps(self, item):
        """
        Adds _created, firstcreated, versioncreated and _updated timestamps
        :param item:
        :return:
        """

        item['firstcreated'] = utc.localize(item['firstcreated'])
        item['versioncreated'] = utc.localize(item['versioncreated'])

    def is_provider_closed(self, provider):
        if provider.get('is_closed', False):
            logger.warning('Ingest Provider %s is closed' % provider.get("name", ""))
            return True
        else:
            return False
