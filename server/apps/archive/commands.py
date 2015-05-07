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
import logging

logger = logging.getLogger(__name__)


class ArchiveRemoveExpiredContent(superdesk.Command):
    """
    Remove expired items form archive after they have been spiked.
    """
    def run(self):
        self.remove_expired_content()

    def remove_expired_content(self):
        logger.info('Removing expired content')
        now = date_to_str(utcnow())
        items = self.get_expired_items(now)
        while items.count() > 0:
            for item in items:
                logger.info('deleting {} expiry: {} now:{}'.format(item['_id'], item['expiry'], now))
                superdesk.get_resource_service('archive').delete_action({'_id': str(item['_id'])})
            items = self.get_expired_items(now)

    def get_expired_items(self, now):
        query_filter = self.get_query_for_expired_items(now)
        req = ParsedRequest()
        req.max_results = 25
        req.args = {'filter': query_filter}
        return superdesk.get_resource_service('archive').get(req, None)

    def get_query_for_expired_items(self, now):
        """
        Return expired items.
        """
        query = {'and':
                 [
                     {'range': {'expiry': {'lte': now}}},
                     {'not': {'term': {'state': 'scheduled'}}}
                 ]
                 }
        return superdesk.json.dumps(query)


superdesk.command('archive:remove_expired', ArchiveRemoveExpiredContent())
