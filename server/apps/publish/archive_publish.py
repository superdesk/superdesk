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

from eve.versioning import resolve_document_version
from eve.utils import config, ParsedRequest
from eve.validation import ValidationError

from apps.content import PUB_STATUS, CONTENT_TYPE, ITEM_TYPE
from apps.publish.subscribers import SUBSCRIBER_TYPES
from settings import DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES
import superdesk
from superdesk.emails import send_article_killed_email
from superdesk.errors import InvalidStateTransitionError, SuperdeskApiError, PublishQueueError
from superdesk.notification import push_notification
from superdesk.services import BaseService
from superdesk import get_resource_service
from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from superdesk.utc import utcnow
from superdesk.workflow import is_workflow_state_transition_valid
from apps.publish.formatters import get_formatter
from apps.common.components.utils import get_component
from apps.item_autosave.components.item_autosave import ItemAutosave
from apps.archive.common import item_url, get_user, insert_into_versions, \
    set_sign_off, SEQUENCE, GUID_FIELD, item_operations, ITEM_OPERATION
from apps.packages import TakesPackageService
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

    def on_update(self, updates, original):
        if original.get('marked_for_not_publication', False):
            raise SuperdeskApiError.badRequestError(
                message='Cannot publish an item which is marked as Not for Publication')

        if not is_workflow_state_transition_valid(self.publish_type, original[config.CONTENT_STATE]):
            raise InvalidStateTransitionError()

        updated = original.copy()
        updates.update(updates)
        validate_item = {'act': self.publish_type, 'type': original['type'], 'validate': updated}
        validation_errors = get_resource_service('validate').post([validate_item])

        if validation_errors[0]:
            raise ValidationError(validation_errors)

    def on_updated(self, updates, original):
        self.update_published_collection(published_item_id=original['_id'])
        original = get_resource_service('archive').find_one(req=None, _id=original['_id'])
        updates.update(original)
        user = get_user()
        push_notification('item:updated', item=str(original['_id']), user=str(user.get('_id')))

    def update(self, id, updates, original):
        """
        Handles workflow of each Publish, Corrected and Killed.
        """
        try:
            user = get_user()
            last_updated = updates.get(config.LAST_UPDATED, utcnow())

            if original[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                self._publish_package_items(original, updates, last_updated)

            set_sign_off(updates, original)
            queued_digital = False
            package_id = None

            if original[ITEM_TYPE] != CONTENT_TYPE.COMPOSITE:
                # if target_for is set the we don't to digital client.
                if not updates.get('targeted_for', original.get('targeted_for')):
                    # check if item is in a digital package
                    package_id = TakesPackageService().get_take_package_id(original)

                    if package_id:
                        queued_digital, takes_package = self._publish_takes_package(package_id, updates,
                                                                                    original, last_updated)
                    else:
                        # if text or preformatted item is going to be sent to digital subscribers, package it as a take
                        if self.sending_to_digital_subscribers(original):
                            # takes packages are only created for these types
                            if original['type'] in (CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED):
                                updated = copy(original)
                                updated.update(updates)
                                # create a takes package
                                package_id = TakesPackageService().package_story_as_a_take(updated, {}, None)
                                original = get_resource_service('archive').find_one(req=None, _id=original['_id'])
                                queued_digital, takes_package = self._publish_takes_package(package_id, updates,
                                                                                            original, last_updated)

                # queue only text items
                queued_wire = \
                    self.publish(doc=original, updates=updates, target_media_type=WIRE if package_id else None)

                queued = queued_digital or queued_wire
                if not queued:
                    raise PublishQueueError.item_not_queued_error(Exception('Nothing is saved to publish queue'), None)

            self._set_version_last_modified_and_state(original, updates, last_updated)
            self._update_archive(original=original, updates=updates, should_insert_into_versions=False)
            push_notification('item:publish', item=str(id), unique_name=original['unique_name'],
                              desk=str(original.get('task', {}).get('desk', '')), user=str(user.get('_id', '')))
        except SuperdeskApiError as e:
            raise e
        except KeyError as e:
            raise SuperdeskApiError.badRequestError(
                message="Key is missing on article to be published: {}".format(str(e)))
        except Exception as e:
            logger.exception("Something bad happened while publishing %s".format(id))
            raise SuperdeskApiError.internalError(message="Failed to publish the item: {}".format(str(e)))

    def _publish_takes_package(self, package_id, updates, original, last_updated):
        """
        Process the takes to form digital master file content and publish.
        :param str package_id: Takes package id
        :param dict updates: updates for the takes packages
        :param dict original: original takes packages document
        :param datetime.datetime last_updated: datetime for the updates
        :return: (bool, dict) boolean flag indicating takes package is queued or not,
                dict containing takes package
        """

        package, package_updates = self.process_takes(updates_of_take_to_be_published=updates,
                                                      original_of_take_to_be_published=original,
                                                      package_id=package_id)

        self._set_version_last_modified_and_state(package, package_updates, last_updated)
        self._update_archive(package, package_updates)
        package.update(package_updates)

        # send it to the digital channels
        queued_digital = self.publish(doc=package, updates=None, target_media_type=DIGITAL)

        self.update_published_collection(published_item_id=package[config.ID_FIELD])
        return queued_digital, package

    def _publish_package_items(self, package, updates, last_updated):
        """
        Publishes items of a package recursively
        :param: package to publish
        :param datetime last_updated: datetime of the updates.
        """
        items = [ref.get('residRef') for group in package.get('groups', [])
                 for ref in group.get('refs', []) if 'residRef' in ref]

        if items:
            archive_publish = get_resource_service('archive_publish')
            for guid in items:
                doc = super().find_one(req=None, _id=guid)
                try:
                    if doc[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                        self._publish_package_items(doc)
                    archive_publish.patch(id=doc.pop('_id'), updates=doc)
                except KeyError:
                    raise SuperdeskApiError.badRequestError("A non-existent content id is requested to publish")
            self.publish(package, updates, target_media_type=DIGITAL)

    def _set_version_last_modified_and_state(self, original, updates, last_updated):
        """
        Sets config.VERSION, config.LAST_UPDATED, config.CONTENT_STATE in updates document.
        :param dict original: original document
        :param dict updates: updates related to the original document
        :param datetime last_updated: datetime of the updates.
        """

        self.set_state(original, updates)
        updates[config.LAST_UPDATED] = last_updated

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
        updates[config.CONTENT_STATE] = self.published_state

    def process_takes(self, updates_of_take_to_be_published, package_id, original_of_take_to_be_published=None):
        """
        Primary rule for publishing a Take in Takes Package is: all previous takes must be published before a take
        can be published.

        This method validates if the take(s) previous to this article are published. If not published then raises error.
        Also, generates body_html of the takes package and make sure the metadata for the package is the same as the
        metadata of the take to be published.

        :param updates_of_take_to_be_published: The take to be published
        :return: Takes Package document and body_html of the Takes Package
        :raises:
            1. Article Not Found Error: If take identified by GUID in the Takes Package is not found in archive.
            2. Previous Take Not Published Error
        """

        package = super().find_one(req=None, _id=package_id)
        body_html = updates_of_take_to_be_published.get('body_html', original_of_take_to_be_published['body_html'])
        package_updates = {'body_html': body_html + '<br>'}

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

            if sequence_num_of_take_to_be_published:
                if self.published_state != "killed":
                    for sequence in range(sequence_num_of_take_to_be_published, 0, -1):
                        previous_take_ref = next(ref for ref in take_refs if ref.get(SEQUENCE) == sequence)
                        if previous_take_ref[GUID_FIELD] != take_article_id:
                            previous_take = super().find_one(req=None, _id=previous_take_ref[GUID_FIELD])

                            if not previous_take:
                                raise PublishQueueError.article_not_found_error(
                                    Exception("Take with id %s not found" % previous_take_ref[GUID_FIELD]))

                            if previous_take and previous_take[config.CONTENT_STATE] not in ['published', 'corrected']:
                                raise PublishQueueError.previous_take_not_published_error(
                                    Exception("Take with id {} is not published in Takes Package with id {}"
                                              .format(previous_take_ref[GUID_FIELD], package[config.ID_FIELD])))

                            package_updates['body_html'] = \
                                previous_take['body_html'] + '<br>' + package_updates['body_html']

                metadata_tobe_copied = ['headline', 'abstract', 'anpa_category', 'pubstatus', 'slugline', 'urgency',
                                        'subject', 'byline', 'dateline', 'publish_schedule']

                for metadata in metadata_tobe_copied:
                    package_updates[metadata] = \
                        updates_of_take_to_be_published.get(metadata, original_of_take_to_be_published.get(metadata))

        return package, package_updates

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
        :return bool: if content is queued then True else False
        :raises PublishQueueError.item_not_queued_error:
                If the nothing is queued.
        """

        queued = True
        no_formatters = []
        updated = doc.copy()

        # Step 1
        if updates:
            desk = None

            if doc.get('task', {}).get('desk'):
                desk = get_resource_service('desks').find_one(req=None, _id=doc['task']['desk'])

            if not doc.get('ingest_provider'):
                updates['source'] = desk['source'] if desk and desk.get('source', '') \
                    else DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES

            updates['pubstatus'] = PUB_STATUS.CANCELED if self.publish_type == 'killed' else PUB_STATUS.USABLE

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
            raise PublishQueueError.item_not_queued_error(Exception('Nothing is saved to publish queue'), None)

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
                            publish_queue_item['item_version'] = doc[config.VERSION] + 1
                            publish_queue_item['formatted_item'] = formatted_doc
                            publish_queue_item['subscriber_id'] = subscriber['_id']
                            publish_queue_item['destination'] = destination
                            publish_queue_item['published_seq_num'] = pub_seq_num
                            publish_queue_item['publish_schedule'] = doc.get('publish_schedule', None)
                            publish_queue_item['unique_name'] = doc.get('unique_name', None)
                            publish_queue_item['content_type'] = doc.get('type', None)
                            publish_queue_item['headline'] = doc.get('headline', None)

                            self.set_state(doc, publish_queue_item)
                            if publish_queue_item.get(config.CONTENT_STATE):
                                publish_queue_item['publishing_action'] = publish_queue_item.get(config.CONTENT_STATE)
                                del publish_queue_item[config.CONTENT_STATE]
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


class ArchivePublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'publish')


class ArchivePublishService(BasePublishService):
    publish_type = 'publish'
    published_state = 'published'

    def set_state(self, original, updates):
        """
        Set the state of the document to schedule if the publish_schedule is specified.
        :param dict original: original document
        :param dict updates: updates related to original document
        """
        updates[ITEM_OPERATION] = ITEM_PUBLISH
        if original.get('publish_schedule') or updates.get('publish_schedule'):
            updates[config.CONTENT_STATE] = 'scheduled'
        else:
            super().set_state(original, updates)

    def get_subscribers(self, doc, target_media_type):
        """
        Get the subscribers for this document based on the target_media_type for publishing.
        1. Get the list of all active subscribers.
        2. If targeted_for is set then exclude internet/digital subscribers.
        3. If takes package then subsequent takes are sent to same wire subscriber as first take.
        4. Filter the subscriber list based on the publish filter and global filters (if configured).
        :param dict doc: Document to publish/correct/kill
        :param str target_media_type: dictate if the doc being queued is a Takes Package or an Individual Article.
                Valid values are - Wire, Digital. If Digital then the doc being queued is a Takes Package and if Wire
                then the doc being queues is an Individual Article.
        :return: (list, list) List of filtered subscriber,
                List of subscribers that have not received item previously (empty list in this case).
        """
        subscribers, subscribers_yet_to_receive = [], []
        first_take = None
        # Step 1
        subscribers = list(get_resource_service('subscribers').get(req=None, lookup={'is_active': True}))

        # Step 2
        if doc.get('targeted_for'):
            subscribers = list(self.non_digital(subscribers))

        # Step 3
        if doc.get(ITEM_TYPE) == CONTENT_TYPE.TEXT or doc.get(ITEM_TYPE) == CONTENT_TYPE.PREFORMATTED:
            first_take = TakesPackageService().get_first_take_in_takes_package(doc)
            if first_take:
                # if first take is published then subsequent takes should to same subscribers.
                query = {'$and': [{'item_id': first_take},
                                  {'publishing_action': {'$in': ['published']}}]}
                subscribers = self._get_subscribers_for_previously_sent_items(query)

        # Step 4
        if not first_take:
            subscribers = self.filter_subscribers(doc, subscribers,
                                                  WIRE if doc.get('targeted_for') else target_media_type)

        return subscribers, subscribers_yet_to_receive


class KillPublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'kill')


class KillPublishService(BasePublishService):
    publish_type = 'kill'
    published_state = 'killed'
    takes_service = TakesPackageService()

    def __init__(self, datasource=None, backend=None):
        super().__init__(datasource=datasource, backend=backend)

    def on_update(self, updates, original):
        updates[ITEM_OPERATION] = ITEM_KILL
        super().on_update(updates, original)
        self.takes_service.process_killed_takes_package(original)

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
        package = self.takes_service.get_take_package(original)
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
                        logger.warn("Could not publish the kill for take {} with headline {}".
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
                          {'publishing_action': {'$in': ['published', 'corrected']}}]}
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
                          {'publishing_action': {'$in': ['published', 'corrected']}}]}

        subscribers = self._get_subscribers_for_previously_sent_items(query)

        if subscribers:
            # step 2
            if not TakesPackageService().get_take_package_id(doc):
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
