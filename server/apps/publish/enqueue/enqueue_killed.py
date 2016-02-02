# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.metadata.item import CONTENT_STATE
from apps.publish.enqueue.enqueue_service import EnqueueService


class EnqueueKilledService(EnqueueService):

    publish_type = 'kill'
    published_state = 'killed'

    def get_subscribers(self, doc, target_media_type):
        """
        Get the subscribers for this document based on the target_media_type for kill.
        Kill is sent to all subscribers that have received the item previously (published or corrected)
        :param doc: Document to kill
        :param target_media_type: dictate if the doc being queued is a Takes Package or an Individual Article.
                Valid values are - Wire, Digital. If Digital then the doc being queued is a Takes Package and if Wire
                then the doc being queued is an Individual Article.
        :return: (list, list) List of filtered subscribers,
                List of subscribers that have not received item previously (empty list in this case).
        """

        subscribers, subscribers_yet_to_receive = [], []
        query = {'$and': [{'item_id': doc['item_id']},
                          {'publishing_action': {'$in': [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]}}]}
        subscribers = self._get_subscribers_for_previously_sent_items(query)

        return subscribers, subscribers_yet_to_receive
