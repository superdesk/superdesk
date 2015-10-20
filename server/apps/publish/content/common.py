# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from copy import copy
from functools import partial
import logging
from copy import deepcopy

from eve.versioning import resolve_document_version
from eve.utils import config, ParsedRequest
from eve.validation import ValidationError

from superdesk.metadata.item import PUB_STATUS, CONTENT_TYPE, ITEM_TYPE, GUID_FIELD, ITEM_STATE, CONTENT_STATE, \
    PUBLISH_STATES, EMBARGO
from superdesk.metadata.packages import SEQUENCE, LINKED_IN_PACKAGES, GROUPS
from superdesk.publish import SUBSCRIBER_TYPES
from settings import DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES
import superdesk
from superdesk.errors import InvalidStateTransitionError, SuperdeskApiError, PublishQueueError
from superdesk.notification import push_notification
from superdesk.services import BaseService
from superdesk import get_resource_service
from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from apps.archive.common import validate_schedule, ITEM_OPERATION, convert_task_attributes_to_objectId
from superdesk.utc import utcnow
from superdesk.workflow import is_workflow_state_transition_valid
from superdesk.publish.formatters import get_formatter
from apps.common.components.utils import get_component
from apps.item_autosave.components.item_autosave import ItemAutosave
from superdesk.metadata.utils import item_url
from apps.archive.common import get_user, insert_into_versions, item_operations
from apps.packages import TakesPackageService
from apps.packages.package_service import PackageService
from apps.publish.published_item import LAST_PUBLISHED_VERSION

logger = logging.getLogger(__name__)

ITEM_PUBLISH = 'publish'
ITEM_CORRECT = 'correct'
ITEM_KILL = 'kill'
item_operations.extend([ITEM_PUBLISH, ITEM_CORRECT, ITEM_KILL])


class BasePublishResource(ArchiveResource):
    """
    Base resource class for "publish" endpoint.
    """

    def __init__(self, endpoint_name, app, service, publish_type):
        self.endpoint_name = 'archive_%s' % publish_type
        self.resource_title = endpoint_name

        self.datasource = {'source': ARCHIVE}

        self.url = 'archive/{}'.format(publish_type)
        self.item_url = item_url

        self.resource_methods = []
        self.item_methods = ['PATCH']

        self.privileges = {'PATCH': publish_type}
        super().__init__(endpoint_name, app=app, service=service)


class BasePublishService(BaseService):
    """
    Base service class for "publish" endpoint
    """

    publish_type = 'publish'
    published_state = 'published'

    non_digital = partial(filter, lambda s: s.get('subscriber_type', '') == SUBSCRIBER_TYPES.WIRE)
    digital = partial(filter, lambda s: (s.get('subscriber_type', '') in {SUBSCRIBER_TYPES.DIGITAL,
                                                                          SUBSCRIBER_TYPES.ALL}))
    takes_package_service = TakesPackageService()
    package_service = PackageService()

    def raise_if_not_marked_for_publication(self, original):
        if original.get('marked_for_not_publication', False):
            raise SuperdeskApiError.badRequestError('Cannot publish an item which is marked as Not for Publication')

    def raise_if_invalid_state_transition(self, original):
        if not is_workflow_state_transition_valid(self.publish_type, original[ITEM_STATE]):
            error_message = "Can't {} as item state is {}" if original[ITEM_TYPE] == CONTENT_TYPE.TEXT else \
                "Can't {} as either package state or one of the items state is {}"
            raise InvalidStateTransitionError(error_message.format(self.publish_type, original[ITEM_STATE]))

    def on_update(self, updates, original):
        self.raise_if_not_marked_for_publication(original)
        self.raise_if_invalid_state_transition(original)

        updated = original.copy()
        updated.update(updates)

        takes_package = self.takes_package_service.get_take_package(original)

        if self.publish_type == 'publish':
            # validate if take can be published
            if takes_package and not self.takes_package_service.can_publish_take(
                    takes_package, updates.get(SEQUENCE, original.get(SEQUENCE, 1))):
                raise PublishQueueError.previous_take_not_published_error(
                    Exception("Previous takes are not published."))

            validate_schedule(updated.get('publish_schedule'), takes_package.get(SEQUENCE, 1) if takes_package else 1)

            if original[ITEM_TYPE] != CONTENT_TYPE.COMPOSITE and updates.get(EMBARGO):
                get_resource_service(ARCHIVE).validate_embargo(updated)

        if self.publish_type in ['correct', 'kill']:
            if updates.get(EMBARGO):
                raise SuperdeskApiError.badRequestError("Embargo can't be set after publishing")

            if updates.get('dateline'):
                raise SuperdeskApiError.badRequestError("Dateline can't be modified after publishing")

        validate_item = {'act': self.publish_type, 'type': original['type'], 'validate': updated}
        validation_errors = get_resource_service('validate').post([validate_item])
        if validation_errors[0]:
            raise ValidationError(validation_errors)

        # validate the package if it is one
        package_validation_errors = []
        self._validate_package_contents(original, takes_package, package_validation_errors)
        if len(package_validation_errors) > 0:
            raise ValidationError(package_validation_errors)

        self._set_updates(original, updates, updates.get(config.LAST_UPDATED, utcnow()))
        updates[ITEM_OPERATION] = ITEM_PUBLISH
        convert_task_attributes_to_objectId(updates)

    def on_updated(self, updates, original):
        self.update_published_collection(published_item_id=original[config.ID_FIELD])
        original = get_resource_service(ARCHIVE).find_one(req=None, _id=original[config.ID_FIELD])
        updates.update(original)
        user = get_user()
        push_notification('item:updated', item=str(original[config.ID_FIELD]), user=str(user.get(config.ID_FIELD)))

    def update(self, id, updates, original):
        """
        Handles workflow of each Publish, Corrected and Killed.
        """
        try:
            user = get_user()
            last_updated = updates.get(config.LAST_UPDATED, utcnow())

            if original[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                self._publish_package_items(original, updates)

            queued_digital = False
            package = None

            if original[ITEM_TYPE] != CONTENT_TYPE.COMPOSITE:
                # if target_for is set the we don't to digital client.
                if not updates.get('targeted_for', original.get('targeted_for')):
                    # check if item is in a digital package
                    package = self.takes_package_service.get_take_package(original)

                    if package:
                        queued_digital = self._publish_takes_package(package, updates, original, last_updated)
                    else:
                        '''
                        If type of the item is text or preformatted then item need to be sent to digital subscribers.
                        So, package the item as a take.
                        '''
                        updated = copy(original)
                        updated.update(updates)

                        if original[ITEM_TYPE] in {CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED} and \
                                self.sending_to_digital_subscribers(updated):
                            # create a takes package
                            package_id = self.takes_package_service.package_story_as_a_take(updated, {}, None)
                            updates[LINKED_IN_PACKAGES] = updated[LINKED_IN_PACKAGES]
                            package = get_resource_service(ARCHIVE).find_one(req=None, _id=package_id)
                            queued_digital = self._publish_takes_package(package, updates, original, last_updated)

                # queue only text items
                media_type = SUBSCRIBER_TYPES.WIRE if package else None
                queued_wire = self.publish(doc=original, updates=updates, target_media_type=media_type)

                queued = queued_digital or queued_wire
                if not queued:
                    logger.exception('Nothing is saved to publish queue for story: {} for action: {}'.
                                     format(original[config.ID_FIELD], self.publish_type))

            self._update_archive(original=original, updates=updates, should_insert_into_versions=False)
            push_notification('item:publish', item=str(id), unique_name=original['unique_name'],
                              desk=str(original.get('task', {}).get('desk', '')),
                              user=str(user.get(config.ID_FIELD, '')))
        except SuperdeskApiError as e:
            raise e
        except KeyError as e:
            raise SuperdeskApiError.badRequestError(
                message="Key is missing on article to be published: {}".format(str(e)))
        except Exception as e:
            logger.exception("Something bad happened while publishing %s".format(id))
            raise SuperdeskApiError.internalError(message="Failed to publish the item: {}".format(str(e)))

    def _publish_takes_package(self, package, updates, original, last_updated):
        """
        Process the takes to form digital master file content and publish.
        :param dict package: Takes package
        :param dict updates: updates for the take
        :param dict original: original takes
        :param datetime.datetime last_updated: datetime for the updates
        :return bool: boolean flag indicating takes package is queued or not
        """

        package_updates = self.process_takes(updates_of_take_to_be_published=updates,
                                             original_of_take_to_be_published=original,
                                             package=package)

        self._set_updates(package, package_updates, last_updated)
        package_updates.setdefault(ITEM_OPERATION, updates.get(ITEM_OPERATION, ITEM_PUBLISH))
        self._update_archive(package, package_updates)

        '''
        When embargo is lapsed and the article should go to Digital Subscribers the BasePublishService creates a
        Takes Package whose state is draft. In this case, we can't initiate post-publish actions on the Takes Package as
        the package hasn't been published. And post-publish service's get_subscribers() will return empty list.
        Also, logically without publishing a package post-publish actions on the item doesn't make sense.
        That's the reason checking the Takes Package state and invoking the appropriate Publish Service.
        '''
        if package[ITEM_STATE] in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]:
            package.update(package_updates)
            queued_digital = self.publish(doc=package, updates=None, target_media_type=SUBSCRIBER_TYPES.DIGITAL)
        else:
            package.update(package_updates)
            queued_digital = get_resource_service('archive_publish').publish(doc=package,
                                                                             updates=None,
                                                                             target_media_type=SUBSCRIBER_TYPES.DIGITAL)

        self.update_published_collection(published_item_id=package[config.ID_FIELD])
        return queued_digital

    def _publish_package_items(self, package, updates):
        """
        Publishes all items of a package recursively then publishes the package itself
        :param package: package to publish
        :param updates: payload
        """
        items = self.package_service.get_residrefs(package)

        if len(items) == 0 and self.publish_type == ITEM_PUBLISH:
            raise SuperdeskApiError.badRequestError("Empty package cannot be published!")

        removed_items = []
        if self.publish_type == ITEM_CORRECT:
            removed_items, added_items = self._get_changed_items(items, updates)
            if len(removed_items) == len(items) and len(added_items) == 0:
                raise SuperdeskApiError.badRequestError("Corrected package cannot be empty!")
            items.extend(added_items)

        subscriber_items = {}
        if items:
            archive_publish = get_resource_service('archive_publish')
            for guid in items:
                package_item = super().find_one(req=None, _id=guid)

                if not package_item:
                    raise SuperdeskApiError.badRequestError(
                        "Package item with id: {} does not exist.".format(guid))

                if package_item[ITEM_STATE] not in PUBLISH_STATES:  # if the item is not published then publish it
                    if package_item[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                        # if the item is a package do recursion to publish
                        sub_updates = {i: updates[i] for i in ['state', 'operation'] if i in updates}
                        sub_updates['groups'] = list(package_item['groups'])
                        self._publish_package_items(package_item, sub_updates)
                        self._update_archive(original=package_item, updates=sub_updates,
                                             should_insert_into_versions=False)
                        self.update_published_collection(published_item_id=package_item[config.ID_FIELD])
                    else:
                        # publish the item
                        archive_publish.patch(id=package_item.pop(config.ID_FIELD), updates=package_item)

                    insert_into_versions(id_=guid)
                    package_item = super().find_one(req=None, _id=guid)

                subscribers = self._get_subscribers_for_package_item(package_item)
                self.package_service.update_field_in_package(updates, package_item[config.ID_FIELD],
                                                             config.VERSION, package_item[config.VERSION])

                if package_item[config.ID_FIELD] in removed_items:
                    digital_item_id = None
                else:
                    digital_item_id = self._get_digital_id_for_package_item(package_item)

                self._extend_subscriber_items(subscriber_items, subscribers, package_item, digital_item_id)

            self.publish_package(package, updates, target_subscribers=subscriber_items)
            return subscribers

    def _extend_subscriber_items(self, subscriber_items, subscribers, item, digital_item_id):
        """
        Extends the subscriber_items with the given list of subscribers for the item
        :param subscriber_items: The existing list of subscribers
        :param subscribers: New subscribers that item has been published to - to be added
        :param item: item that has been published
        :param digital_item_id: digital_item_id
        """
        item_id = item[config.ID_FIELD]
        for subscriber in subscribers:
            sid = subscriber[config.ID_FIELD]
            item_list = subscriber_items.get(sid, {}).get('items', {})
            item_list[item_id] = digital_item_id
            subscriber_items[sid] = {'subscriber': subscriber, 'items': item_list}

    def _get_changed_items(self, existing_items, updates):
        """
        Returns the added and removed items from existing_items
        :param existing_items: Existing list
        :param updates: Changes
        :return: list of removed items and list of added items
        """
        if 'groups' in updates:
            new_items = self.package_service.get_residrefs(updates)
            removed_items = list(set(existing_items) - set(new_items))
            added_items = list(set(new_items) - set(existing_items))
            return removed_items, added_items
        else:
            return [], []

    def _get_digital_id_for_package_item(self, package_item):
        """
        Finds the digital item id for a given item in a package
        :param package_item: item in a package
        :return string: Digital item id if there's one otherwise id of package_item
        """
        if package_item[ITEM_TYPE] not in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            return package_item[config.ID_FIELD]
        else:
            package_item_takes_package_id = self.takes_package_service.get_take_package_id(package_item)
            if not package_item_takes_package_id:
                return package_item[config.ID_FIELD]
            return package_item_takes_package_id

    def _get_subscribers_for_package_item(self, package_item):
        """
        Finds the list of subscribers for a given item in a package
        :param package_item: item in a package
        :return list: List of subscribers
        :return string: Digital item id if there's one otherwise None
        """
        if package_item[ITEM_TYPE] not in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            query = {'$and': [{'item_id': package_item[config.ID_FIELD]},
                              {'publishing_action': package_item[ITEM_STATE]}]}
        else:
            package_item_takes_package = self.takes_package_service.get_take_package(package_item)
            if not package_item_takes_package:
                # this item has not been published to digital subscribers so
                # the list of subscribers are empty
                return []

            query = {'$and': [{'item_id': package_item_takes_package[config.ID_FIELD]},
                              {'publishing_action': package_item_takes_package[ITEM_STATE]}]}

        return self._get_subscribers_for_previously_sent_items(query)

    def _set_updates(self, original, updates, last_updated):
        """
        Sets config.VERSION, config.LAST_UPDATED, ITEM_STATE in updates document.
        If item is being published and embargo is available then append Editorial Note with 'Embargoed'.

        :param dict original: original document
        :param dict updates: updates related to the original document
        :param datetime last_updated: datetime of the updates.
        """

        self.set_state(original, updates)
        updates.setdefault(config.LAST_UPDATED, last_updated)

        if original[config.VERSION] == updates.get(config.VERSION, original[config.VERSION]):
            resolve_document_version(document=updates, resource=ARCHIVE, method='PATCH', latest_doc=original)

        if updates.get(EMBARGO, original.get(EMBARGO)) \
                and updates.get('ednote', original.get('ednote', '')).find('Embargo') == -1:
            updates['ednote'] = '{} {}'.format(original.get('ednote', ''), 'Embargoed.').strip()

    def _update_archive(self, original, updates, versioned_doc=None, should_insert_into_versions=True):
        """
        Updates the articles into archive collection and inserts the latest into archive_versions.
        Also clears autosaved versions if any.
        :param: versioned_doc: doc which can be inserted into archive_versions
        :param: should_insert_into_versions if True inserts the latest document into versions collection
        """

        self.backend.update(self.datasource, original[config.ID_FIELD], updates, original)

        if should_insert_into_versions:
            if versioned_doc is None:
                insert_into_versions(id_=original[config.ID_FIELD])
            else:
                insert_into_versions(doc=versioned_doc)

        get_component(ItemAutosave).clear(original[config.ID_FIELD])

    def set_state(self, original, updates):
        """
        Set the state of the document based on the action (publish, correction, kill)
        :param dict original: original document
        :param dict updates: updates related to document
        """
        updates['publish_schedule'] = None
        updates[ITEM_STATE] = self.published_state

    def process_takes(self, updates_of_take_to_be_published, package, original_of_take_to_be_published=None):
        """
        Primary rule for publishing a Take in Takes Package is: all previous takes must be published before a take
        can be published.

        Also, generates body_html of the takes package and make sure the metadata for the package is the same as the
        metadata of the take to be published.

        :param dict updates_of_take_to_be_published: updates for the take to be published
        :param dict package: Takes package to publish
        :param dict original_of_take_to_be_published: original of the take to be published
        :return: Takes Package Updates
        """

        takes = self.takes_package_service.get_published_takes(package)
        body_html = updates_of_take_to_be_published.get('body_html', original_of_take_to_be_published['body_html'])
        package_updates = {}

        groups = package.get(GROUPS, [])
        if groups:
            take_refs = [ref for group in groups if group['id'] == 'main' for ref in group.get('refs')]
            sequence_num_of_take_to_be_published = 0

            take_article_id = updates_of_take_to_be_published.get(
                config.ID_FIELD, original_of_take_to_be_published[config.ID_FIELD])

            for r in take_refs:
                if r[GUID_FIELD] == take_article_id:
                    sequence_num_of_take_to_be_published = r[SEQUENCE]
                    break

            if takes and self.published_state != 'killed':
                body_html_list = [take.get('body_html', '') for take in takes]
                if self.published_state == 'published':
                    body_html_list.append(body_html)
                else:
                    body_html_list[sequence_num_of_take_to_be_published - 1] = body_html

                package_updates['body_html'] = '<br>'.join(body_html_list)
            else:
                package_updates['body_html'] = body_html

            metadata_tobe_copied = self.takes_package_service.fields_for_creating_take.copy()
            metadata_tobe_copied.extend(['publish_schedule', 'byline'])
            updated_take = original_of_take_to_be_published.copy()
            updated_take.update(updates_of_take_to_be_published)
            metadata_from = updated_take
            if self.published_state == 'corrected' and len(takes) > 1:
                # get the last take metadata only if there are more than one takes
                metadata_from = takes[-1]

            for metadata in metadata_tobe_copied:
                package_updates[metadata] = metadata_from.get(metadata)

            package_updates[GROUPS] = groups
            self.package_service.update_field_in_package(package_updates,
                                                         original_of_take_to_be_published[config.ID_FIELD],
                                                         config.VERSION,
                                                         updates_of_take_to_be_published[config.VERSION])

        return package_updates

    def publish_package(self, package, updates, target_subscribers):
        """
        Publishes a given non-take package to given subscribers.
        For each subscriber updates the package definition with the wanted_items for that subscriber
        and removes unwanted_items that doesn't supposed to go that subscriber.
        Text stories are replaced by the digital versions.
        :param package: Package to be published
        :param updates: Updates to the package
        :param target_subscribers: List of subscriber and items-per-subscriber
        """
        self._process_publish_updates(package, updates)
        all_items = self.package_service.get_residrefs(package)
        for items in target_subscribers.values():
            updated = deepcopy(package)
            updates_copy = deepcopy(updates)
            updated.update(updates_copy)
            subscriber = items['subscriber']
            wanted_items = [item for item in items['items'] if items['items'].get(item, None)]
            unwanted_items = [item for item in all_items if item not in wanted_items]
            for i in unwanted_items:
                still_items_left = self.package_service.remove_ref_from_inmem_package(updated, i)
                if not still_items_left and self.publish_type != 'correct':
                    # if nothing left in the package to be published and
                    # if not correcting then don't send the package
                    return
            for key in wanted_items:
                self.package_service.replace_ref_in_package(updated, key, items['items'][key])
            self.queue_transmission(updated, [subscriber])

    def _process_publish_updates(self, doc, updates):
        """ Common updates for published items """
        desk = None
        if doc.get('task', {}).get('desk'):
            desk = get_resource_service('desks').find_one(req=None, _id=doc['task']['desk'])
        if not doc.get('ingest_provider'):
            updates['source'] = desk['source'] if desk and desk.get('source', '') \
                else DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES
        updates['pubstatus'] = PUB_STATUS.CANCELED if self.publish_type == 'kill' else PUB_STATUS.USABLE

    def publish(self, doc, updates, target_media_type=None):
        """
        Queue the content for publishing.
        1. Sets the Metadata Properties - source and pubstatus
        2. Get the subscribers.
        3. Update the headline of wire stories with the sequence
        4. Queue the content for subscribers
        5. Queue the content for previously published subscribers if any.
        6. Sends notification if no formatter has found for any of the formats configured in Subscriber.
        7. If not queued and not formatters then raise exception.
        :param dict doc: document to publish
        :param dict updates: updates for the document
        :param str target_media_type: dictate if the doc being queued is a Takes Package or an Individual Article.
                Valid values are - Wire, Digital. If Digital then the doc being queued is a Takes Package and if Wire
                then the doc being queues is an Individual Article.
        :param dict target_subscribers: list of subscribers that document needs to get sent
        :return bool: if content is queued then True else False
        :raises PublishQueueError.item_not_queued_error:
                If the nothing is queued.
        """

        queued = True
        no_formatters = []
        updated = doc.copy()

        # Step 1
        if updates:
            self._process_publish_updates(doc, updates)
            updated.update(updates)

        # Step 2
        subscribers, subscribers_yet_to_receive = self.get_subscribers(doc, target_media_type)

        # Step 3
        if target_media_type == SUBSCRIBER_TYPES.WIRE:
            self._update_headline_sequence(updated)

        # Step 4
        no_formatters, queued = self.queue_transmission(updated, subscribers)

        # Step 5
        if subscribers_yet_to_receive:
            formatters_not_found, queued_new_subscribers = self.queue_transmission(updated, subscribers_yet_to_receive)
            no_formatters.extend(formatters_not_found)
            queued = queued or queued_new_subscribers

        # Step 6
        user = get_user()
        if len(no_formatters) > 0:
            push_notification('item:publish:wrong:format',
                              item=str(doc[config.ID_FIELD]), unique_name=doc['unique_name'],
                              desk=str(doc.get('task', {}).get('desk', '')),
                              user=str(user.get(config.ID_FIELD, '')),
                              formats=no_formatters)

        # Step 7
        if not target_media_type and not queued:
            logger.exception('Nothing is saved to publish queue for story: {} for action: {}'.
                             format(doc[config.ID_FIELD], self.publish_type))

        return queued

    def sending_to_digital_subscribers(self, doc):
        """
        Returns False if item has embargo and is in future.
        Returns True if there is a digital subscriber either in the previously sent or in yet to be sent subscribers

        :param doc: document
        :return bool: True if there's at least one
        """

        if doc.get(EMBARGO) and doc.get(EMBARGO) > utcnow():
            return False

        subscribers, subscribers_yet_to_receive = self.get_subscribers(doc, SUBSCRIBER_TYPES.DIGITAL)
        subscribers = list(self.digital(subscribers))
        subscribers_yet_to_receive = list(self.digital(subscribers_yet_to_receive))
        return len(subscribers) > 0 or len(subscribers_yet_to_receive) > 0

    def get_subscribers(self, doc, target_media_type):
        """
        Get subscribers for doc based on target_media_type.
        Override this method in the ArchivePublishService, ArchiveCorrectService and ArchiveKillService
        :param doc: Document to publish/correct/kill
        :param target_media_type: dictate if the doc being queued is a Takes Package or an Individual Article.
                Valid values are - Wire, Digital. If Digital then the doc being queued is a Takes Package and if Wire
                then the doc being queues is an Individual Article.
        :return: (list, list) List of filtered subscriber,
                List of subscribers that have not received item previously (empty list in this case).
        """
        raise NotImplementedError()

    def _get_subscribers_for_previously_sent_items(self, lookup):
        """
        Returns list of subscribers that have previously received the item.
        :param dict lookup: elastic query to filter the publish queue
        :return: list of subscribers
        """
        req = ParsedRequest()
        subscribers = []
        queued_items = get_resource_service('publish_queue').get(req=req, lookup=lookup)
        if queued_items.count():
            subscriber_ids = {queued_item['subscriber_id'] for queued_item in queued_items}
            query = {'$and': [{config.ID_FIELD: {'$in': list(subscriber_ids)}}]}
            subscribers = list(get_resource_service('subscribers').get(req=None, lookup=query))
        return subscribers

    def filter_subscribers(self, doc, subscribers, target_media_type):
        """
        Filter subscribers to whom the current document is going to be delivered.
        :param doc: Document to publish/kill/correct
        :param subscribers: List of Subscribers that might potentially get this document
        :param target_media_type: dictate if the doc being queued is a Takes Package or an Individual Article.
                Valid values are - Wire, Digital. If Digital then the doc being queued is a Takes Package and if Wire
                then the doc being queues is an Individual Article.
        :return: List of of filtered subscriber.
        """
        filtered_subscribers = []
        req = ParsedRequest()
        req.args = {'is_global': True}
        service = get_resource_service('content_filters')
        global_filters = list(service.get(req=req, lookup=None))

        for subscriber in subscribers:
            if target_media_type and subscriber.get('subscriber_type', '') != SUBSCRIBER_TYPES.ALL:
                can_send_takes_packages = subscriber['subscriber_type'] == SUBSCRIBER_TYPES.DIGITAL
                if target_media_type == SUBSCRIBER_TYPES.WIRE and can_send_takes_packages or \
                   target_media_type == SUBSCRIBER_TYPES.DIGITAL and not can_send_takes_packages:
                    continue

            if doc.get('targeted_for'):
                found_match = [t for t in doc['targeted_for'] if t['name'] == subscriber.get('subscriber_type', '')]

                if len(found_match) == 0 and subscriber.get('geo_restrictions'):
                    found_match = [t for t in doc['targeted_for'] if t['name'] == subscriber['geo_restrictions']]
                    if len(found_match) == 0 or found_match[0]['allow'] is False:
                        continue
                elif len(found_match) > 0 and found_match[0]['allow'] is False:
                    continue

            if not self.conforms_global_filter(subscriber, global_filters, doc):
                continue

            if not self.conforms_content_filter(subscriber, doc):
                continue

            filtered_subscribers.append(subscriber)

        return filtered_subscribers

    def queue_transmission(self, doc, subscribers):
        """
        Method formats and then queues the article for transmission to the passed subscribers.
        ::Important Note:: Format Type across Subscribers can repeat. But we can't have formatted item generated once
        based on the format_types configured across for all the subscribers as the formatted item must have a published
        sequence number generated by Subscriber.
        :param dict doc: document to queue for transmission
        :param list subscribers: List of subscriber dict.
        :return : (list, bool) tuple of list of missing formatters and boolean flag. True if queued else False
        """

        try:
            queued = False
            no_formatters = []
            for subscriber in subscribers:
                try:
                    if doc[ITEM_TYPE] not in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED] and \
                            subscriber.get('subscriber_type', '') == SUBSCRIBER_TYPES.WIRE:
                        # wire subscribers can get only text and preformatted stories
                        continue

                    for destination in subscriber['destinations']:
                        # Step 2(a)
                        formatter = get_formatter(destination['format'], doc)

                        if not formatter:  # if formatter not found then record it
                            no_formatters.append(destination['format'])
                            continue

                        formatted_docs = formatter.format(doc, subscriber)

                        for pub_seq_num, formatted_doc in formatted_docs:
                            publish_queue_item = dict()
                            publish_queue_item['item_id'] = doc['_id']
                            publish_queue_item['item_version'] = doc[config.VERSION]
                            publish_queue_item['formatted_item'] = formatted_doc
                            publish_queue_item['subscriber_id'] = subscriber['_id']
                            publish_queue_item['destination'] = destination
                            publish_queue_item['published_seq_num'] = pub_seq_num
                            publish_queue_item['publish_schedule'] = doc.get('publish_schedule', None)
                            publish_queue_item['unique_name'] = doc.get('unique_name', None)
                            publish_queue_item['content_type'] = doc.get('type', None)
                            publish_queue_item['headline'] = doc.get('headline', None)

                            self.set_state(doc, publish_queue_item)
                            if publish_queue_item.get(ITEM_STATE):
                                publish_queue_item['publishing_action'] = publish_queue_item.get(ITEM_STATE)
                                del publish_queue_item[ITEM_STATE]
                            else:
                                publish_queue_item['publishing_action'] = self.published_state

                            get_resource_service('publish_queue').post([publish_queue_item])
                            queued = True
                except:
                    logger.exception("Failed to queue item for id {} with headline {} for subscriber {}."
                                     .format(doc.get(config.ID_FIELD), doc.get('headline'), subscriber.get('name')))

            return no_formatters, queued
        except:
            raise

    def update_published_collection(self, published_item_id):
        """
        Updates the published collection with the published item.
        Set the last_published_version to false for previous versions of the published items.
        :param: str published_item_id: _id of the document.
        """
        published_item = super().find_one(req=None, _id=published_item_id)
        published_item = copy(published_item)
        get_resource_service('published').update_published_items(published_item_id, LAST_PUBLISHED_VERSION, False)
        get_resource_service('published').post([published_item])

    def conforms_content_filter(self, subscriber, doc):
        """
        Checks if the document matches the subscriber filter
        :param subscriber: Subscriber to get the filter
        :param doc: Document to test the filter against
        :return:
        True if there's no filter
        True if matches and permitting
        False if matches and blocking
        False if doesn't match and permitting
        True if doesn't match and blocking
        """
        content_filter = subscriber.get('content_filter')

        if content_filter is None or 'filter_id' not in content_filter or content_filter['filter_id'] is None:
            return True

        service = get_resource_service('content_filters')
        filter = service.find_one(req=None, _id=content_filter['filter_id'])
        does_match = service.does_match(filter, doc)

        if does_match:
            return content_filter['filter_type'] == 'permitting'
        else:
            return content_filter['filter_type'] == 'blocking'

    def conforms_global_filter(self, subscriber, global_filters, doc):
        """
        Checks if subscriber has a override rule against each of the
        global filter and if not checks if document matches the global filter
        :param subscriber: Subscriber to get if the global filter is overriden
        :param global_filters: List of all global filters
        :param doc: Document to test the global filter against
        :return: True if at least one global filter is not overriden
        and it matches the document
        False if global filter matches the document or all of them overriden
        """
        service = get_resource_service('content_filters')
        gfs = subscriber.get('global_filters', {})
        for global_filter in global_filters:
            if gfs.get(str(global_filter['_id']), True):
                # Global filter applies to this subscriber
                if service.does_match(global_filter, doc):
                    # All global filters behaves like blocking filters
                    return False
        return True

    def _update_headline_sequence(self, doc):
        """ Updates the headline of the text story if there's any sequence value in it """
        if doc.get(SEQUENCE):
            doc['headline'] = '{}={}'.format(doc['headline'], doc.get(SEQUENCE))

    def _validate_package_contents(self, package, takes_package, validation_errors=[]):
        """
        If the item passed is a package this function will ensure that the unpublished content validates and none of
        the content is locked by other than the publishing session, also do not allow any killed or spiked content

        :param package:
        :param takes_package:
        :param validation_errors: validation errors are appended if there are any.
        """
        # Ensure it is the sort of thing we need to validate
        if package[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE and not takes_package and self.publish_type == ITEM_PUBLISH:
            items = self.package_service.get_residrefs(package)

            # make sure package is not scheduled or spiked
            if package[ITEM_STATE] in (CONTENT_STATE.SPIKED, CONTENT_STATE.SCHEDULED):
                validation_errors.append('Package cannot be {}'.format(package[ITEM_STATE]))

            if package.get(EMBARGO):
                validation_errors.append('Package cannot have Embargo')

            if items:
                for guid in items:
                    doc = super().find_one(req=None, _id=guid)

                    if package[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                        digital = self.takes_package_service.get_take_package(doc) or {}
                        self._validate_package_contents(doc, digital, validation_errors)

                    # make sure no items are killed or spiked or scheduled
                    if doc[ITEM_STATE] in (CONTENT_STATE.KILLED, CONTENT_STATE.SPIKED, CONTENT_STATE.SCHEDULED):
                        validation_errors.append('Package cannot contain {} item'.format(doc[ITEM_STATE]))

                    if doc.get(EMBARGO):
                        validation_errors.append('Package cannot have Items with Embargo')

                    # don't validate items that already have published
                    if doc[ITEM_STATE] not in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]:
                        validate_item = {'act': self.publish_type, 'type': doc[ITEM_TYPE], 'validate': doc}
                        errors = get_resource_service('validate').post([validate_item], headline=True)
                        if errors[0]:
                            validation_errors.extend(errors[0])

                    # check the locks on the items
                    if doc.get('lock_session', None) and package['lock_session'] != doc['lock_session']:
                        validation_errors.extend(['{}: packaged item cannot be locked'.format(doc['headline'])])

superdesk.workflow_state('published')
superdesk.workflow_action(
    name='publish',
    include_states=['fetched', 'routed', 'submitted', 'in_progress', 'scheduled'],
    privileges=['publish']
)

superdesk.workflow_state('scheduled')
superdesk.workflow_action(
    name='schedule',
    include_states=['fetched', 'routed', 'submitted', 'in_progress'],
    privileges=['schedule']
)

superdesk.workflow_action(
    name='deschedule',
    include_states=['scheduled'],
    privileges=['deschedule']
)

superdesk.workflow_state('killed')
superdesk.workflow_action(
    name='kill',
    include_states=['published', 'scheduled', 'corrected'],
    privileges=['kill']
)

superdesk.workflow_state('corrected')
superdesk.workflow_action(
    name='correct',
    include_states=['published', 'corrected'],
    privileges=['correct']
)

superdesk.workflow_action(
    name='rewrite',
    include_states=['published', 'corrected'],
    privileges=['rewrite']
)
