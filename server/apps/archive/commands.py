# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from eve.utils import ParsedRequest, date_to_str
import superdesk
from superdesk.utc import utcnow
from .archive import SOURCE as ARCHIVE
import logging

logger = logging.getLogger(__name__)


class RemoveExpiredSpikeContent(superdesk.Command):
    """
    Removes expired articles whose state is 'spiked' form archive.
    """

    def run(self):
        self.remove_expired_content()

    def remove_expired_content(self):
        logger.info('Removing expired content if spiked')

        now = date_to_str(utcnow())
        items = self.get_expired_items(now)

        while items.count() > 0:
            for item in items:
                logger.info('deleting {} expiry: {} now:{}'.format(item['_id'], item['expiry'], now))
                superdesk.get_resource_service(ARCHIVE).remove_expired(item)

            items = self.get_expired_items(now)

    def get_expired_items(self, now):
        query_filter = self._get_query_for_expired_items(now)
        req = ParsedRequest()
        req.max_results = 100

        return superdesk.get_resource_service(ARCHIVE).get_from_mongo(req=req, lookup=query_filter)

    def _get_query_for_expired_items(self, now):
        query = {
            '$and': [
                {'expiry': {'$lte': now}},
                {'state': 'spiked'}
            ]
        }

        return query


superdesk.command('archive:remove_spiked_if_expired', RemoveExpiredSpikeContent())
