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
import logging

from eve.versioning import resolve_document_version
from eve.utils import config
from eve.validation import ValidationError

from settings import DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES
import superdesk
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
    set_sign_off, PUBLISH_STATES, SEQUENCE, GUID_FIELD, \
    item_operations, ITEM_OPERATION
from apps.packages import TakesPackageService

logger = logging.getLogger(__name__)

DIGITAL = 'digital'
WIRE = 'wire'
ITEM_PUBLISH = 'publish'
ITEM_CORRECT = 'correct'
ITEM_KILL = 'kill'
item_operations.append(ITEM_PUBLISH)


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

    def on_update(self, updates, original):
        if original.get('marked_for_not_publication', False):
            raise SuperdeskApiError.badRequestError(
                message='Cannot publish an item which is marked as Not for Publication')

        if not is_workflow_state_transition_valid(self.publish_type, original[config.CONTENT_STATE]):
            raise InvalidStateTransitionError()

        # TODO: Does this hit any time??? If not whats the use of this???
        if original.get('item_id') and get_resource_service('published').is_published_before(original['item_id']):
            raise PublishQueueError.post_publish_exists_error(Exception('Story with id:{}'.format(original['_id'])))

        validate_item = {'act': self.publish_type, 'type': original['type'], 'validate': updates}
        validation_errors = get_resource_service('validate').post([validate_item])

        if validation_errors[0]:
            raise ValidationError(validation_errors)

    def on_updated(self, updates, original):
        self.update_published_collection(published_item_id=original['_id'])
        user = get_user()
        push_notification('item:updated', item=str(original['_id']), user=str(user.get('_id')))

    def update(self, id, updates, original):
        """
        Handles workflow of each Publish, Corrected and Killed.
        """

        try:
            last_updated = updates.get(config.LAST_UPDATED, utcnow())

            if original['type'] == 'composite':
                self._publish_package_items(original, last_updated)

            set_sign_off(updates, original)

            if original['type'] != 'composite':
                # check if item is in a digital package
                package_id = TakesPackageService().get_take_package_id(original)

                if package_id:
                    # process the takes to form digital master file content
                    package, package_updates = self.process_takes(updates_of_take_to_be_published=updates,
                                                                  original_of_take_to_be_published=original,
                                                                  package_id=package_id)

                    self._set_version_last_modified_and_state(package, package_updates, last_updated)
                    self._update_archive(package, package_updates)
                    package.update(package_updates)

                    # send it to the digital channels
                    queued_digital = self.publish(doc=package, updates=None, target_output_channels=DIGITAL)

                    self.update_published_collection(published_item_id=package[config.ID_FIELD])
                else:
                    queued_digital = False

                # queue only text items
                queued_wire = \
                    self.publish(doc=original, updates=updates, target_output_channels=WIRE if package_id else None)

                queued = queued_digital or queued_wire
                if not queued:
                    raise PublishQueueError.item_not_queued_error(Exception('Nothing is saved to publish queue'), None)

            user = get_user()
            self._set_version_last_modified_and_state(original, updates, last_updated)
            self._update_archive(original=original, updates=updates)
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

        resolve_document_version(document=updates, resource=ARCHIVE, method='PATCH', latest_doc=original)

    def _update_archive(self, original, updates, versioned_doc=None):
        """
        Updates the articles into archive collection and inserts the latest into archive_versions.
        Also clears autosaved versions if any.
        :param versioned_doc: doc which can be inserted into archive_versions
        """

        self.backend.update(self.datasource, original[config.ID_FIELD], updates, original)

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

                metadata_tobe_copied = ['headline', 'abstract', 'anpa-category', 'pubstatus', 'slugline', 'urgency',
                                        'subject']
                for metadata in metadata_tobe_copied:
                    package_updates[metadata] = \
                        updates_of_take_to_be_published.get(metadata, original_of_take_to_be_published.get(metadata))

        return package, package_updates

    def publish(self, doc, updates, target_output_channels=None):
        """
        Queues the article, sets the final Source and sends notification if no formatter has found for any
        of the formats configured in Subscriber.
        """

        no_formatters, queued = \
            self.queue_transmission(doc=doc, target_output_channels=target_output_channels)

        if updates:
            desk = None

            if doc.get('task', {}).get('desk'):
                desk = get_resource_service('desks').find_one(req=None, _id=doc['task']['desk'])

            if not doc.get('ingest_provider'):
                updates['source'] = desk['source'] if desk and desk.get('source', '') \
                    else DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES

        user = get_user()

        if no_formatters and len(no_formatters) > 0:
            push_notification('item:publish:wrong:format',
                              item=str(doc['_id']), unique_name=doc['unique_name'],
                              desk=str(doc.get('task', {}).get('desk', '')),
                              user=str(user.get('_id', '')),
                              formats=no_formatters)

        if not target_output_channels and not queued:
            raise PublishQueueError.item_not_queued_error(Exception('Nothing is saved to publish queue'), None)

        return queued

    def queue_transmission(self, doc, target_output_channels=None):
        """
        Formats and queues the article to all active subscribers. Workflow:
            1. Fetch Active Subscribers
            2. For each Destination of a Subscriber,
                a. format the article as per the format defined in the destination.
                b. queue the formatted article
        :return:
            1. format list for which formatters are not found,
            2. True if the article queued for transmissions False otherwise.
        """

        try:
            queued = False
            no_formatters = []

            # Step 1
            subscribers = get_resource_service('subscribers').get(req=None, lookup={'is_active': True})

            for subscriber in subscribers:
                can_send_takes_packages = subscriber.get('can_send_takes_packages', False)
                if target_output_channels == WIRE and can_send_takes_packages or target_output_channels == DIGITAL \
                        and not can_send_takes_packages:
                    continue

                if not self.conforms_publish_filter(subscriber, doc):
                    continue

                # Step 2
                for destination in subscriber['destinations']:
                    # Step 2(a)
                    formatter = get_formatter(destination['format'], doc['type'])

                    if not formatter:  # if formatter not found then record it
                        no_formatters.append(destination['format'])
                        continue

                    pub_seq_num, formatted_doc = formatter.format(doc, subscriber)

                    # Step 2(b)
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


class ArchivePublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'publish')


class ArchivePublishService(BasePublishService):
    publish_type = 'publish'
    published_state = 'published'

    def set_state(self, original, updates):
        updates[ITEM_OPERATION] = ITEM_PUBLISH
        if (original.get('publish_schedule') or updates.get('publish_schedule')) \
                and original[config.CONTENT_STATE] not in PUBLISH_STATES:
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
