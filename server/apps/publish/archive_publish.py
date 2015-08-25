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
    PUBLISH_STATES
from superdesk.metadata.packages import SEQUENCE, PACKAGE_TYPE, TAKES_PACKAGE, LINKED_IN_PACKAGES
from apps.publish.subscribers import SUBSCRIBER_TYPES
from settings import DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES
import superdesk
from superdesk.emails import send_article_killed_email
from superdesk.errors import InvalidStateTransitionError, SuperdeskApiError, PublishQueueError
from superdesk.notification import push_notification
from superdesk.services import BaseService
from superdesk import get_resource_service
from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from apps.archive.common import validate_schedule, is_item_in_package
from superdesk.utc import utcnow
from superdesk.workflow import is_workflow_state_transition_valid
from apps.publish.formatters import get_formatter
from apps.common.components.utils import get_component
from apps.item_autosave.components.item_autosave import ItemAutosave
from apps.archive.common import item_url, get_user, insert_into_versions, \
    set_sign_off, item_operations, ITEM_OPERATION
from apps.packages import TakesPackageService
from apps.packages.package_service import PackageService
from apps.publish.published_item import LAST_PUBLISHED_VERSION

logger = logging.getLogger(__name__)

DIGITAL = 'digital'
WIRE = 'wire'
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

    non_digital = partial(filter, lambda s: s.get('subscriber_type', '') != SUBSCRIBER_TYPES.DIGITAL)
    digital = partial(filter, lambda s: s.get('subscriber_type', '') == SUBSCRIBER_TYPES.DIGITAL)
    takes_package_service = TakesPackageService()
    package_service = PackageService()

    def on_update(self, updates, original):
        if original.get('marked_for_not_publication', False):
            raise SuperdeskApiError.badRequestError(
                message='Cannot publish an item which is marked as Not for Publication')

        if not is_workflow_state_transition_valid(self.publish_type, original[ITEM_STATE]):
            error_message = "Can't {} as item state is {}" if original[ITEM_TYPE] == CONTENT_TYPE.TEXT else \
                "Can't {} as either package state or one of the items state is {}"
            raise InvalidStateTransitionError(error_message.format(self.publish_type, original[ITEM_STATE]))

        updated = original.copy()
        updated.update(updates)
        validate_item = {'act': self.publish_type, 'type': original['type'], 'validate': updated}

        takes_package = self.takes_package_service.get_take_package(original) or {}
        # validate if take can be published
        if self.publish_type == 'publish' and takes_package \
            and not self.takes_package_service.can_publish_take(takes_package,
                                                                updates.get(SEQUENCE, original.get(SEQUENCE, 1))):
            raise PublishQueueError.previous_take_not_published_error(
                Exception("Previous takes are not published."))

        # validate the publish schedule
        validate_schedule(updated.get('publish_schedule'), takes_package.get(SEQUENCE, 1))
        validation_errors = get_resource_service('validate').post([validate_item])

        if validation_errors[0]:
            raise ValidationError(validation_errors)

        # validate the package if it is one
        self._validate_package_contents(original, takes_package)
        self._set_version_last_modified_and_state(original, updates, updates.get(config.LAST_UPDATED, utcnow()))

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
                        # if text or preformatted item is going to be sent to digital subscribers, package it as a take
                        if self.sending_to_digital_subscribers(original):
                            # takes packages are only created for these types
                            if original[ITEM_TYPE] in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
                                updated = copy(original)
                                updated.update(updates)
                                # create a takes package
                                package_id = self.takes_package_service.package_story_as_a_take(updated, {}, None)
                                updates[LINKED_IN_PACKAGES] = updated[LINKED_IN_PACKAGES]
                                package = get_resource_service(ARCHIVE).find_one(req=None, _id=package_id)
                                queued_digital = self._publish_takes_package(package, updates,
                                                                             original, last_updated)

                # queue only text items
                queued_wire = \
                    self.publish(doc=original, updates=updates, target_media_type=WIRE if package else None)

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

        self._set_version_last_modified_and_state(package, package_updates, last_updated)
        self._update_archive(package, package_updates)
        package.update(package_updates)

        # send it to the digital channels
        queued_digital = self.publish(doc=package, updates=None, target_media_type=DIGITAL)

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

                if package_item[ITEM_STATE] not in PUBLISH_STATES:
                    # if the item is not published then publish it

                    if package_item[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                        # if the item is a package do recursion to publish
                        self._publish_package_items(package_item, updates)
                        self._update_archive(original=package_item, updates=updates, should_insert_into_versions=False)
                        self.update_published_collection(published_item_id=package_item[config.ID_FIELD])
                    else:
                        # publish the item
                        archive_publish.patch(id=package_item.pop(config.ID_FIELD), updates=package_item)

                    package_item = super().find_one(req=None, _id=guid)

                subscribers = self._get_subscribers_for_package_item(package_item)

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

    def _set_version_last_modified_and_state(self, original, updates, last_updated):
        """
        Sets config.VERSION, config.LAST_UPDATED, ITEM_STATE in updates document.
        :param dict original: original document
        :param dict updates: updates related to the original document
        :param datetime last_updated: datetime of the updates.
        """

        self.set_state(original, updates)
        updates.setdefault(config.LAST_UPDATED, last_updated)

        if original[config.VERSION] == updates.get(config.VERSION, original[config.VERSION]):
            resolve_document_version(document=updates, resource=ARCHIVE, method='PATCH', latest_doc=original)

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

        groups = package.get('groups', [])
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

            metadata_tobe_copied = ['headline', 'abstract', 'anpa_category', 'pubstatus', 'slugline', 'urgency',
                                    'subject', 'byline', 'dateline', 'publish_schedule']

            updated_take = original_of_take_to_be_published.copy()
            updated_take.update(updates_of_take_to_be_published)
            metadata_from = updated_take
            if self.published_state == 'corrected' and len(takes) > 1:
                # get the last take metadata only if there are more than one takes
                metadata_from = takes[-1]

            for metadata in metadata_tobe_copied:
                package_updates[metadata] = metadata_from.get(metadata)

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
        all_items = PackageService().get_residrefs(package)
        for items in target_subscribers.values():
            updated = deepcopy(package)
            updates_copy = deepcopy(updates)
            updated.update(updates_copy)
            subscriber = items['subscriber']
            wanted_items = [item for item in items['items'] if items['items'].get(item, None)]
            unwanted_items = [item for item in all_items if item not in wanted_items]
            for i in unwanted_items:
                still_items_left = PackageService().remove_ref_from_inmem_package(updated, i)
                if not still_items_left and self.publish_type != 'correct':
                    # if nothing left in the package to be published and
                    # if not correcting then don't send the package
                    return
            for key in wanted_items:
                PackageService().replace_ref_in_package(updated, key, items['items'][key])
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
        if target_media_type == WIRE:
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
        subscribers, subscribers_yet_to_receive = self.get_subscribers(doc, DIGITAL)
        return len(subscribers) > 0

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
        service = get_resource_service('publish_filters')
        global_filters = list(service.get(req=req, lookup=None))

        for subscriber in subscribers:
            if target_media_type:
                can_send_takes_packages = subscriber['subscriber_type'] == SUBSCRIBER_TYPES.DIGITAL
                if target_media_type == WIRE and can_send_takes_packages or target_media_type == DIGITAL \
                        and not can_send_takes_packages:
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

            if not self.conforms_publish_filter(subscriber, doc):
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

    def conforms_publish_filter(self, subscriber, doc):
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
        publish_filter = subscriber.get('publish_filter')

        if publish_filter is None or 'filter_id' not in publish_filter or publish_filter['filter_id'] is None:
            return True

        service = get_resource_service('publish_filters')
        filter = service.find_one(req=None, _id=publish_filter['filter_id'])
        does_match = service.does_match(filter, doc)

        if does_match:
            return publish_filter['filter_type'] == 'permitting'
        else:
            return publish_filter['filter_type'] == 'blocking'

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
        service = get_resource_service('publish_filters')
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

    def _validate_package_contents(self, package, takes_package):
        """
        If the item passed is a package this function will ensure that the unpublished content validates and none of
         the content is locked by other than the publishing session, also do not allow any killed or spiked content
        :param package:
        :param takes_package:
        :raises: Validation exceptions if the validation fails
        """
        # Ensure it is the sort of thing we need to validate
        if package[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE and not takes_package and self.publish_type == ITEM_PUBLISH:
            items = self.package_service.get_residrefs(package)

            validation_errors = []
            if items:
                for guid in items:
                    doc = super().find_one(req=None, _id=guid)
                    # make sure no items are killed or locked
                    if doc[ITEM_STATE] in (CONTENT_STATE.KILLED, CONTENT_STATE.SPIKED):
                        raise ValidationError(['Package contains killed or spike item'])
                    # don't validate items that already have published
                    if doc[ITEM_STATE] not in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]:
                        validate_item = {'act': self.publish_type, 'type': doc[ITEM_TYPE], 'validate': doc}
                        errors = get_resource_service('validate').post([validate_item], headline=True)
                        if errors[0]:
                            validation_errors.extend(errors[0])
                    # check the locks on the items
                    if doc.get('lock_session', None) and package['lock_session'] != doc['lock_session']:
                        validation_errors.extend(['{}: packaged item is locked'.format(doc['headline'])])
                if len(validation_errors) > 0:
                    raise ValidationError(validation_errors)


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
        updates[ITEM_OPERATION] = ITEM_PUBLISH
        if original.get('publish_schedule') or updates.get('publish_schedule'):
            updates[ITEM_STATE] = CONTENT_STATE.SCHEDULED
        else:
            super().set_state(original, updates)

    def get_subscribers(self, doc, target_media_type):
        """
        Get the subscribers for this document based on the target_media_type for publishing.
        1. Get the list of all active subscribers.
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
        subscribers = list(get_resource_service('subscribers').get(req=None, lookup={'is_active': True}))

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
                                                  WIRE if doc.get('targeted_for') else target_media_type)

        if takes_subscribers:
            # Step 4a
            subscribers_ids = set(s[config.ID_FIELD] for s in takes_subscribers)
            subscribers = takes_subscribers + [s for s in subscribers if s[config.ID_FIELD] not in subscribers_ids]

        return subscribers, subscribers_yet_to_receive


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
        updates[ITEM_OPERATION] = ITEM_KILL
        super().on_update(updates, original)
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
                    queued = self.publish(doc=original_data, updates=updates_data, target_media_type=WIRE)
                    # we need to update the archive item and not worry about queued as we could have
                    # a takes only going to digital client.
                    self._set_version_last_modified_and_state(original_data, updates_data, last_updated)
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


class CorrectPublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'correct')


class CorrectPublishService(BasePublishService):
    publish_type = 'correct'
    published_state = 'corrected'

    def on_update(self, updates, original):
        updates[ITEM_OPERATION] = ITEM_CORRECT
        super().on_update(updates, original)
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
        packages = PackageService().get_packages(original[config.ID_FIELD])
        if packages and packages.count() > 0:
            archive_correct = get_resource_service('archive_correct')
            processed_packages = []
            for package in packages:
                if package[ITEM_STATE] in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED] and \
                        package.get(PACKAGE_TYPE, '') == '' and \
                        str(package[config.ID_FIELD]) not in processed_packages:
                    archive_correct.patch(id=package[config.ID_FIELD], updates=original_updates)
                    processed_packages.append(package[config.ID_FIELD])

    def get_subscribers(self, doc, target_media_type):
        """
        Get the subscribers for this document based on the target_media_type
        for article Correction.
        1. The article is sent to Subscribers (digital and wire) who has received the article previously.
        2. For subsequent takes, only published to previously published wire clients. Digital clients don't get
           individual takes but digital client takes package.
        3. Fetch Active Subscribers and exclude those who received the article previously.
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
                active_subscribers = get_resource_service('subscribers').get(req=None, lookup={'is_active': True})
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
                                            WIRE if doc.get('targeted_for') else target_media_type)

        return subscribers, subscribers_yet_to_receive


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
