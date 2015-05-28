# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from eve.utils import ParsedRequest, date_to_str
import superdesk
from superdesk.utc import utcnow
import logging

logger = logging.getLogger(__name__)


class RemoveExpiredPublishContent(superdesk.Command):
    """
    Remove expired items from published.
    """
    def run(self):
        self.remove_expired_content()

    def remove_expired_content(self):
        logger.info('Removing expired content from published')
        now = date_to_str(utcnow())
        items = self.get_expired_items(now)

        while items.count() > 0:
            for item in items:
                logger.info('deleting article of type {} with id {} and headline {} -- expired on: {} now: {}'.
                            format(item['type'], item['_id'], item['headline'], item['expiry'], now))

                superdesk.get_resource_service('published').remove_expired(item)

            items = self.get_expired_items(now)

    def get_expired_items(self, now):
        logger.info('Get expired content from published')
        query_filter = self.get_query_for_expired_items(now)
        req = ParsedRequest()
        req.sort = '_created'
        req.max_results = 100
        return superdesk.get_resource_service('published').get_from_mongo(req=req, lookup=query_filter)

    def get_query_for_expired_items(self, now):
        query = {
            '$and': [
                {'expiry': {'$lte': now}},
                {'state': {'$ne': 'scheduled'}}
            ]
        }
        return query

superdesk.command('publish:remove_expired', RemoveExpiredPublishContent())
