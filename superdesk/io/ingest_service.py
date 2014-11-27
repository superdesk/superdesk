from superdesk.utc import utc


class IngestService():
    """Base ingest service class."""

    def get_items(self, guid):
        raise LookupError()

    def update(self, provider):
        raise NotImplementedError()

    def add_timestamps(self, item):
        """
        Adds _created, firstcreated, versioncreated and _updated timestamps
        :param item:
        :return:
        """

        item['firstcreated'] = utc.localize(item['firstcreated'])
        item['versioncreated'] = utc.localize(item['versioncreated'])
