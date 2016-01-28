# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import get_resource_service
from superdesk.metadata.item import EMBARGO, CONTENT_STATE
from superdesk.publish import SUBSCRIBER_TYPES
from superdesk.utc import utcnow

from eve.utils import config

from apps.publish.enqueue.enqueue_service import EnqueueService


class EnqueueCorrectedService(EnqueueService):
    def get_subscribers(self, doc, target_media_type):
        """
        Get the subscribers for this document based on the target_media_type for article Correction.
        1. The article is sent to Subscribers (digital and wire) who has received the article previously.
        2. For subsequent takes, only published to previously published wire clients. Digital clients don't get
           individual takes but digital client takes package.
        3. If the item has embargo and is a future date then fetch active Wire Subscribers.
           Otherwise fetch Active Subscribers. After fetching exclude those who received the article previously from
           active subscribers list.
        4. If article has 'targeted_for' property then exclude subscribers of type Internet from Subscribers list.
        5. Filter the subscriber that have not received the article previously against publish filters
        and global filters for this document.
        :param doc: Document to correct
        :param target_media_type: dictate if the doc being queued is a Takes Package or an Individual Article.
                Valid values are - Wire, Digital. If Digital then the doc being queued is a Takes Package and if Wire
                then the doc being queues is an Individual Article.
        :return: (list, list) List of filtered subscribers, List of subscribers that have not received item previously
        """
        subscribers, subscribers_yet_to_receive = [], []
        # step 1
        query = {'$and': [{'item_id': doc['item_id']},
                          {'publishing_action': {'$in': [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]}}]}

        subscribers = self._get_subscribers_for_previously_sent_items(query)

        if subscribers:
            # step 2
            if not self.takes_package_service.get_take_package_id(doc):
                # Step 3
                query = {'is_active': True}
                if doc.get(EMBARGO) and doc.get(EMBARGO) > utcnow():
                    query['subscriber_type'] = SUBSCRIBER_TYPES.WIRE

                active_subscribers = list(get_resource_service('subscribers').get(req=None, lookup=query))
                subscribers_yet_to_receive = [a for a in active_subscribers
                                              if not any(a[config.ID_FIELD] == s[config.ID_FIELD]
                                                         for s in subscribers)]

            if len(subscribers_yet_to_receive) > 0:
                # Step 4
                if doc.get('targeted_for'):
                    subscribers_yet_to_receive = list(self.non_digital(subscribers_yet_to_receive))
                # Step 5
                subscribers_yet_to_receive = \
                    self.filter_subscribers(doc, subscribers_yet_to_receive,
                                            SUBSCRIBER_TYPES.WIRE if doc.get('targeted_for') else target_media_type)

        return subscribers, subscribers_yet_to_receive
