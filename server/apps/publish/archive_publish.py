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

from apps.content import PUB_STATUS
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

    def on_update(self, updates, original):
        if original.get('marked_for_not_publication', False):
            raise SuperdeskApiError.badRequestError(
                message='Cannot publish an item which is marked as Not for Publication')

        if not is_workflow_state_transition_valid(self.publish_type, original[config.CONTENT_STATE]):
            raise InvalidStateTransitionError()

        if original.get('item_id') and get_resource_service('published').is_published_before(original['item_id']):
            raise PublishQueueError.post_publish_exists_error(Exception('Story with id:{}'.format(original['_id'])))

        validate_item = {'act': self.publish_type, 'type': original['type'], 'validate': updates}
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

            if original['type'] == 'composite':
                self._publish_package_items(original, last_updated)

            set_sign_off(updates, original)
            queued_digital = False

            if original['type'] != 'composite':
                # check if item is in a digital package
                package_id = TakesPackageService().get_take_package_id(original)

                if package_id:
                    queued_digital = self._publish_takes_package(package_id, updates, original, last_updated)
                else:
                    # if item is going to be sent to digital subscribers, package it as a take
                    if self.sending_to_digital_subscribers(updates):
                        updated = copy(original)
                        updated.update(updates)
                        # create a takes package
                        package_id = TakesPackageService().package_story_as_a_take(updated, {}, None)
                        original = get_resource_service('archive').find_one(req=None, _id=original['_id'])
                        queued_digital = self._publish_takes_package(package_id, updates, original, last_updated)

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
        # process the takes to form digital master file content
        package, package_updates = self.process_takes(updates_of_take_to_be_published=updates,
                                                      original_of_take_to_be_published=original,
                                                      package_id=package_id)

        self._set_version_last_modified_and_state(package, package_updates, last_updated)
        self._update_archive(package, package_updates)
        package.update(package_updates)

        # send it to the digital channels
        queued_digital = self.publish(doc=package, updates=None, target_media_type=DIGITAL)

        self.update_published_collection(published_item_id=package[config.ID_FIELD])
        return queued_digital

    def _publish_package_items(self, package, last_updated):
        """
        Publishes items of a package recursively
        """

        items = [ref.get('residRef') for group in package.get('groups', [])
                 for ref in group.get('refs', []) if 'residRef' in ref]

        if items:
            for guid in items:
                doc = super().find_one(req=None, _id=guid)
                try:
                    if doc['type'] == 'composite':
                        self._publish_package_items(doc)

                    original = copy(doc)

                    set_sign_off(doc, original)

                    self._set_version_last_modified_and_state(original, doc, last_updated)
                    self._update_archive(original, {config.CONTENT_STATE: doc[config.CONTENT_STATE],
                                                    config.ETAG: doc[config.ETAG],
                                                    config.VERSION: doc[config.VERSION],
                                                    config.LAST_UPDATED: doc[config.LAST_UPDATED],
                                                    'sign_off': doc['sign_off']},
                                         versioned_doc=doc)
                except KeyError:
                    raise SuperdeskApiError.badRequestError("A non-existent content id is requested to publish")

    def _set_version_last_modified_and_state(self, original, updates, last_updated):
        """
        Sets config.VERSION, config.LAST_UPDATED, config.CONTENT_STATE in updates document.
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
                                        'subject', 'byline', 'dateline']

                for metadata in metadata_tobe_copied:
                    package_updates[metadata] = \
                        updates_of_take_to_be_published.get(metadata, original_of_take_to_be_published.get(metadata))

        return package, package_updates

    def publish(self, doc, updates, target_media_type=None):
        """
        1. Sets the Metadata Properties - source and pubstatus
        2. Formats and queues the article to subscribers based on the state of the article:
            a. If the state of the article is killed then:
                i.  An email should be sent to all Subscribers irrespective of their status.
                ii. The article should be formatted as per the type of the format and then queue article to the
                    Subscribers who received the article previously.
            b. If the state of the article is corrected then:
                i.      The article should be formatted as per the type of the format and then queue article to the
                        Subscribers who received the article previously.
                ii.     Fetch Active Subscribers and exclude those who received the article previously.
                iii.    If article has 'targeted_for' property then exclude subscribers of type Internet from
                        Subscribers list.
                iv.     For each subscriber in the list, check if the article matches against publish filters and
                        global filters if configured for the subscriber. If matches then the article should be formatted
                        as per the type of the format and then queue article to the subscribers.
            c. If the state of the article is published then:
                i.     Fetch Active Subscribers.
                ii.    If article has 'targeted_for' property then exclude subscribers of type Internet from
                       Subscribers list.
                iii.    For each subscriber in the list, check if the article matches against publish filters and global
                        filters if configured for the subscriber. If matches then the article should be formatted
                        as per the type of the format and then queue article.
        3. Sends notification if no formatter has found for any of the formats configured in Subscriber.
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

        # Step 2(a)
        if self.published_state == 'killed':
            req = ParsedRequest()
            req.sort = '[("completed_at", 1)]'
            queued_items = get_resource_service('publish_queue').get(
                req=req, lookup={'item_id': updated[config.ID_FIELD]})

            if queued_items.count():
                queued_items = list(queued_items)

                # Step 2(a)(i)
                subscribers = list(get_resource_service('subscribers').get(req=None, lookup=None))
                recipients = [s.get('email') for s in subscribers if s.get('email')]
                send_article_killed_email(doc, recipients, queued_items[0].get('completed_at'))

                # Step 2(a)(ii)
                no_formatters, queued = self.queue_transmission(updated, subscribers, None)
        elif self.published_state == 'corrected':  # Step 2(b)
            subscribers, subscribers_yet_to_receive = self.get_subscribers(updated)
            if subscribers:
                no_formatters, queued = self.queue_transmission(updated, subscribers)

                if subscribers_yet_to_receive:
                    # Step 2(b)(iv)
                    formatters_not_found, queued_new_subscribers = \
                        self.queue_transmission(updated, subscribers_yet_to_receive, target_media_type)
                    no_formatters.extend(formatters_not_found)
        elif self.published_state == 'published':  # Step 2(c)
            subscribers, subscribers_yet_to_receive = self.get_subscribers(updated)

            # Step 2(c)(iii)
            no_formatters, queued = self.queue_transmission(updated, subscribers, target_media_type)

        # Step 3
        user = get_user()
        if len(no_formatters) > 0:
            push_notification('item:publish:wrong:format',
                              item=str(doc[config.ID_FIELD]), unique_name=doc['unique_name'],
                              desk=str(doc.get('task', {}).get('desk', '')),
                              user=str(user.get(config.ID_FIELD, '')),
                              formats=no_formatters)

        if not target_media_type and not queued:
            raise PublishQueueError.item_not_queued_error(Exception('Nothing is saved to publish queue'), None)

        return queued

    def sending_to_digital_subscribers(self, doc):
        subscribers, subscribers_yet_to_receive = self.get_subscribers(doc)
        filtered_subscribers = self.filter_subscribers(doc, subscribers, DIGITAL)
        return len(filtered_subscribers) > 0

    def get_subscribers(self, doc):
        subscribers, subscribers_yet_to_receive = [], []
        if self.published_state == 'corrected':
            query = {'$and': [{'item_id': doc[config.ID_FIELD]}, {'publishing_action': 'published'}]}
            queued_items = get_resource_service('publish_queue').get(req=None, lookup=query)

            if queued_items.count():
                # Step 2(b)(i)
                queued_items = list(queued_items)
                subscriber_ids = {queued_item['subscriber_id'] for queued_item in queued_items}

                query = {'$and': [{config.ID_FIELD: {'$in': list(subscriber_ids)}}]}
                subscribers = list(get_resource_service('subscribers').get(req=None, lookup=query))
                if subscribers:
                    # Step 2(b)(ii)
                    active_subscribers = get_resource_service('subscribers').get(req=None, lookup={'is_active': True})
                    subscribers_yet_to_receive = [a for a in active_subscribers
                                                  if not any(a[config.ID_FIELD] == s[config.ID_FIELD]
                                                             for s in subscribers)]

                    if len(subscribers_yet_to_receive) > 0:
                        # Step 2(b)(iii)
                        if doc.get('targeted_for'):
                            subscribers_yet_to_receive = list(self.non_digital(subscribers_yet_to_receive))

        elif self.published_state == 'published':  # Step 2(c)
            # Step 2(c)(i)
            subscribers = list(get_resource_service('subscribers').get(req=None, lookup={'is_active': True}))

            # Step 2(c)(ii)
            if doc.get('targeted_for'):
                subscribers = list(self.non_digital(subscribers))

        return subscribers, subscribers_yet_to_receive

    def filter_subscribers(self, doc, subscribers, target_media_type):
        """
        Filter subscribers to whom the current story is going to be delivered.
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
                matching_target = [t for t in doc.get('targeted_for')
                                   if t['name'] == subscriber.get('subscriber_type', '') or
                                   t['name'] == subscriber.get('geo_restrictions', '')]

                if len(matching_target) > 0 and matching_target[0]['allow'] is False:
                    continue

            if not self.conforms_global_filter(subscriber, global_filters, doc):
                continue
            if not self.conforms_publish_filter(subscriber, doc):
                continue

            filtered_subscribers.append(subscriber)

        return filtered_subscribers

    def queue_transmission(self, doc, subscribers, target_media_type=None):
        """
        Method formats and then queues the article for transmission to the passed subscribers.
        ::Important Note:: Format Type across Subscribers can repeat. But we can't have formatted item generated once
        based on the format_types configured across for all the subscribers as the formatted item must have a published
        sequence number generated by Subscriber.

        :param: target_media_type - dictate if the doc being queued is a Takes Package or an Individual Article.
                Valid values are - Wire, Digital. If Digital then the doc being queued is a Takes Package and if Wire
                then the doc being queues is an Individual Article.
        """

        try:
            queued = False
            no_formatters = []
            for subscriber in self.filter_subscribers(doc, subscribers, target_media_type):
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

            return no_formatters, queued
        except:
            raise

    def update_published_collection(self, published_item_id):
        """
        Updates the published collection with the published item.
        """

        published_item = super().find_one(req=None, _id=published_item_id)
        get_resource_service('published').update_published_items(published_item_id, 'last_publish_action',
                                                                 self.published_state)
        get_resource_service('published').post([copy(published_item)])

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

        if not publish_filter or 'filter_id' not in publish_filter:
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


class ArchivePublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'publish')


class ArchivePublishService(BasePublishService):
    publish_type = 'publish'
    published_state = 'published'

    def set_state(self, original, updates):
        updates[ITEM_OPERATION] = ITEM_PUBLISH
        if original.get('publish_schedule') or updates.get('publish_schedule'):
            updates[config.CONTENT_STATE] = 'scheduled'
        else:
            super().set_state(original, updates)


class KillPublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'kill')


class KillPublishService(BasePublishService):
    publish_type = 'kill'
    published_state = 'killed'

    def __init__(self, datasource=None, backend=None):
        super().__init__(datasource=datasource, backend=backend)

    def on_update(self, updates, original):
        updates[ITEM_OPERATION] = ITEM_KILL
        super().on_update(updates, original)
        TakesPackageService().process_killed_takes_package(original)


class CorrectPublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'correct')


class CorrectPublishService(BasePublishService):
    publish_type = 'correct'
    published_state = 'corrected'

    def on_update(self, updates, original):
        updates[ITEM_OPERATION] = ITEM_CORRECT
        super().on_update(updates, original)


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
