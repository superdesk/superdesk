from .common import BasePublishService, BasePublishResource, ITEM_KILL
from eve.utils import config
from superdesk.metadata.item import CONTENT_STATE, GUID_FIELD, PUB_STATUS
from superdesk import get_resource_service
from superdesk.publish import SUBSCRIBER_TYPES
from superdesk.utc import utcnow
import logging
from copy import copy
from superdesk.emails import send_article_killed_email
from superdesk.errors import SuperdeskApiError
from apps.archive.common import is_item_in_package, ITEM_OPERATION

logger = logging.getLogger(__name__)


class KillPublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'kill')


class KillPublishService(BasePublishService):
    publish_type = 'kill'
    published_state = 'killed'

    def __init__(self, datasource=None, backend=None):
        super().__init__(datasource=datasource, backend=backend)

    def on_update(self, updates, original):
        # check if we are trying to kill and item that is contained in normal non takes package
        if is_item_in_package(original):
            raise SuperdeskApiError.badRequestError(message='This item is in a package' +
                                                            ' it needs to be removed before the item can be killed')
        updates['pubstatus'] = PUB_STATUS.CANCELED
        super().on_update(updates, original)
        updates[ITEM_OPERATION] = ITEM_KILL
        self.takes_package_service.process_killed_takes_package(original)

    def update(self, id, updates, original):
        """
        Kill will broadcast kill email notice to all subscriber in the system and then kill the item.
        If item is a take then all the takes are killed as well.
        """
        self._broadcast_kill_email(original)
        super().update(id, updates, original)
        self._publish_kill_for_takes(updates, original)

    def _broadcast_kill_email(self, original):
        """
        Sends the broadcast email to all subscribers (including in-active subscribers)
        :param original: Document to kill
        """
        # Get all subscribers
        subscribers = list(get_resource_service('subscribers').get(req=None, lookup=None))
        recipients = [s.get('email') for s in subscribers if s.get('email')]
        # send kill email.
        send_article_killed_email(original, recipients, utcnow())

    def _publish_kill_for_takes(self, updates, original):
        """
        Kill all the takes in a takes package.
        :param updates: Updates of the original document
        :param original: Document to kill
        """
        package = self.takes_package_service.get_take_package(original)
        last_updated = updates.get(config.LAST_UPDATED, utcnow())
        if package:
            for ref in[ref for group in package.get('groups', []) if group['id'] == 'main'
                       for ref in group.get('refs')]:
                if ref[GUID_FIELD] != original[config.ID_FIELD]:
                    original_data = super().find_one(req=None, _id=ref[GUID_FIELD])
                    updates_data = copy(updates)
                    queued = self.publish(doc=original_data,
                                          updates=updates_data,
                                          target_media_type=SUBSCRIBER_TYPES.WIRE)
                    # we need to update the archive item and not worry about queued as we could have
                    # a takes only going to digital client.
                    self._set_updates(original_data, updates_data, last_updated)
                    self._update_archive(original=original_data, updates=updates_data,
                                         should_insert_into_versions=True)
                    self.update_published_collection(published_item_id=original_data['_id'])

                    if not queued:
                        logger.exception("Could not publish the kill for take {} with headline {}".
                                         format(original_data.get(config.ID_FIELD), original_data.get('headline')))

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
        query = {'$and': [{'item_id': doc[config.ID_FIELD]},
                          {'publishing_action': {'$in': [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]}}]}
        subscribers = self._get_subscribers_for_previously_sent_items(query)

        return subscribers, subscribers_yet_to_receive
