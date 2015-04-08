# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
import superdesk

from datetime import datetime
from superdesk.utc import utc, utcnow
from superdesk.errors import SuperdeskApiError, SuperdeskIngestError


logger = logging.getLogger(__name__)


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
            try:
                return self._update(provider) or []
            except SuperdeskIngestError as ex:
                if provider.get('critical_errors', {}).get(str(ex.code)):
                    update = {
                        'is_closed': True,
                        'last_closed': {
                            'closed_at': utcnow(),
                            'message': 'Channel closed due to critical error: {}'.format(ex)
                        }
                    }

                    ingest_service = superdesk.get_resource_service('ingest_providers')
                    ingest_service.system_update(provider[superdesk.config.ID_FIELD], update, provider)
                raise ex

    def add_timestamps(self, item):
        """Adds firstcreated and versioncreated timestamps

        :param item:
        """
        item['firstcreated'] = utc.localize(item['firstcreated']) if item.get('firstcreated') else utcnow()
        item['versioncreated'] = utc.localize(item['versioncreated']) if item.get('versioncreated') else utcnow()

    def log_item_error(self, err, item, provider):
        """TODO: put item into provider error basket."""
        logger.warning('ingest error msg={} item={} provider={}'.format(
            str(err),
            item.get('guid'),
            provider.get('name')
        ))
