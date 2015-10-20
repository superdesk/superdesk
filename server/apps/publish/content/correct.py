from .common import BasePublishService, BasePublishResource, ITEM_CORRECT
from eve.utils import config
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE, EMBARGO
from superdesk.metadata.packages import PACKAGE_TYPE
from superdesk.publish import SUBSCRIBER_TYPES
from superdesk import get_resource_service
from superdesk.utc import utcnow
from apps.archive.common import set_sign_off, ITEM_OPERATION, insert_into_versions
from apps.archive.archive_crop import ArchiveCropService
import logging

logger = logging.getLogger(__name__)


class CorrectPublishResource(BasePublishResource):

    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'correct')


class CorrectPublishService(BasePublishService):
    publish_type = 'correct'
    published_state = 'corrected'

    def on_update(self, updates, original):
        ArchiveCropService().validate_multiple_crops(updates, original)
        super().on_update(updates, original)
        updates[ITEM_OPERATION] = ITEM_CORRECT
        set_sign_off(updates, original)

    def on_updated(self, updates, original):
        """
        Locates the published or corrected non-take packages containing the corrected item
        and corrects them
        :param updates: correction
        :param original: original story
        """
        original_updates = dict()
        original_updates['operation'] = updates['operation']
        original_updates[ITEM_STATE] = updates[ITEM_STATE]
        super().on_updated(updates, original)
        ArchiveCropService().delete_replaced_crop_files(updates, original)
        packages = self.package_service.get_packages(original[config.ID_FIELD])
        if packages and packages.count() > 0:
            archive_correct = get_resource_service('archive_correct')
            processed_packages = []
            for package in packages:
                if package[ITEM_STATE] in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED] and \
                        package.get(PACKAGE_TYPE, '') == '' and \
                        str(package[config.ID_FIELD]) not in processed_packages:
                    original_updates['groups'] = package['groups']

                    if updates.get('headline'):
                        self.package_service.update_field_in_package(original_updates, original[config.ID_FIELD],
                                                                     'headline', updates.get('headline'))

                    if updates.get('slugline'):
                        self.package_service.update_field_in_package(original_updates, original[config.ID_FIELD],
                                                                     'slugline', updates.get('slugline'))

                    archive_correct.patch(id=package[config.ID_FIELD], updates=original_updates)
                    insert_into_versions(id_=package[config.ID_FIELD])
                    processed_packages.append(package[config.ID_FIELD])

    def update(self, id, updates, original):
        ArchiveCropService().create_multiple_crops(updates, original)
        super().update(id, updates, original)

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
        query = {'$and': [{'item_id': doc[config.ID_FIELD]},
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
