from .common import BasePublishService, BasePublishResource, ITEM_PUBLISH
from eve.utils import config
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE, ITEM_STATE, CONTENT_STATE, EMBARGO
from superdesk.metadata.packages import PACKAGE_TYPE, TAKES_PACKAGE
from superdesk.publish import SUBSCRIBER_TYPES
from superdesk import get_resource_service
from superdesk.utc import utcnow
from apps.archive.common import set_sign_off, ITEM_OPERATION
import logging

logger = logging.getLogger(__name__)


class ArchivePublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'publish')


class ArchivePublishService(BasePublishService):
    publish_type = 'publish'
    published_state = 'published'

    def on_update(self, updates, original):
        super().on_update(updates, original)
        set_sign_off(updates, original)

    def set_state(self, original, updates):
        """
        Set the state of the document to schedule if the publish_schedule is specified.
        :param dict original: original document
        :param dict updates: updates related to original document
        """

        updates.setdefault(ITEM_OPERATION, ITEM_PUBLISH)
        if original.get('publish_schedule') or updates.get('publish_schedule'):
            updates[ITEM_STATE] = CONTENT_STATE.SCHEDULED
        else:
            super().set_state(original, updates)

    def get_subscribers(self, doc, target_media_type):
        """
        Get the subscribers for this document based on the target_media_type for publishing.
        1. If the item has embargo and is a future date then fetch active Wire Subscribers.
           Otherwise get all active subscribers.
            a. Get the list of takes subscribers if Takes Package
        2. If targeted_for is set then exclude internet/digital subscribers.
        3. If takes package then subsequent takes are sent to same wire subscriber as first take.
        4. Filter the subscriber list based on the publish filter and global filters (if configured).
            a. Publish to takes package subscribers if the takes package is received by the subscriber.
        :param dict doc: Document to publish/correct/kill
        :param str target_media_type: dictate if the doc being queued is a Takes Package or an Individual Article.
                Valid values are - Wire, Digital. If Digital then the doc being queued is a Takes Package and if Wire
                then the doc being queues is an Individual Article.
        :return: (list, list) List of filtered subscriber,
                List of subscribers that have not received item previously (empty list in this case).
        """
        subscribers, subscribers_yet_to_receive, takes_subscribers = [], [], []
        first_take = None

        # Step 1
        query = {'is_active': True}
        if doc.get(EMBARGO) and doc.get(EMBARGO) > utcnow():
            query['subscriber_type'] = SUBSCRIBER_TYPES.WIRE

        subscribers = list(get_resource_service('subscribers').get(req=None, lookup=query))

        if doc.get(ITEM_TYPE) in [CONTENT_TYPE.COMPOSITE] and doc.get(PACKAGE_TYPE) == TAKES_PACKAGE:
            # Step 1a
            query = {'$and': [{'item_id': doc[config.ID_FIELD]},
                              {'publishing_action': {'$in': [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]}}]}
            takes_subscribers = self._get_subscribers_for_previously_sent_items(query)

        # Step 2
        if doc.get('targeted_for'):
            subscribers = list(self.non_digital(subscribers))

        # Step 3
        if doc.get(ITEM_TYPE) in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            first_take = self.takes_package_service.get_first_take_in_takes_package(doc)
            if first_take:
                # if first take is published then subsequent takes should to same subscribers.
                query = {'$and': [{'item_id': first_take},
                                  {'publishing_action': {'$in': [CONTENT_STATE.PUBLISHED]}}]}
                subscribers = self._get_subscribers_for_previously_sent_items(query)

        # Step 4
        if not first_take:
            subscribers = self.filter_subscribers(doc, subscribers,
                                                  SUBSCRIBER_TYPES.WIRE if doc.get('targeted_for')
                                                  else target_media_type)

        if takes_subscribers:
            # Step 4a
            subscribers_ids = set(s[config.ID_FIELD] for s in takes_subscribers)
            subscribers = takes_subscribers + [s for s in subscribers if s[config.ID_FIELD] not in subscribers_ids]

        return subscribers, subscribers_yet_to_receive
