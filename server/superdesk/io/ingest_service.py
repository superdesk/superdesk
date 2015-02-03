# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from datetime import datetime
from superdesk.utc import utc
from superdesk.errors import SuperdeskApiError


class IngestService():
    """Base ingest service class."""

    def get_items(self, guid):
        raise LookupError()

    def _update(self, provider):
        raise NotImplementedError()

    def update(self, provider):
        is_closed = provider.get('is_closed', False)
        if isinstance(is_closed, datetime):
            is_closed = False
        if is_closed:
            raise SuperdeskApiError.internalError('Ingest Provider is closed')
        else:
            return self._update(provider) or []

    def add_timestamps(self, item):
        """
        Adds _created, firstcreated, versioncreated and _updated timestamps
        :param item:
        :return:
        """

        item['firstcreated'] = utc.localize(item['firstcreated'])
        item['versioncreated'] = utc.localize(item['versioncreated'])
