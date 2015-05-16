# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.versioning import resolve_document_version
from eve.utils import config, document_etag
from eve.validation import ValidationError
from copy import copy
import logging

import superdesk
from superdesk.errors import InvalidStateTransitionError, SuperdeskApiError, PublishQueueError
from superdesk.notification import push_notification
from superdesk.services import BaseService
from superdesk import get_resource_service

from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from superdesk.workflow import is_workflow_state_transition_valid
from apps.publish.formatters import get_formatter
from apps.common.components.utils import get_component
from apps.item_autosave.components.item_autosave import ItemAutosave
from apps.archive.common import item_url, get_user, insert_into_versions, \
    set_sign_off, PUBLISH_STATES
from apps.archive.takes_package_service import TakesPackageService


logger = logging.getLogger(__name__)

DIGITAL = 'digital'
WIRE = 'wire'


class BasePublishResource(ArchiveResource):
    """
    Resource class for "publish" endpoint.
    """
    def __init__(self, endpoint_name, app, service, publish_type):
        self.endpoint_name = 'archive_' + publish_type
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
        if not is_workflow_state_transition_valid(self.publish_type, original[config.CONTENT_STATE]):
            raise InvalidStateTransitionError()
        if original.get('item_id') and get_resource_service('published').is_published_before(original['item_id']):
            raise PublishQueueError.post_publish_exists_error(Exception('Story with id:{}'.format(original['_id'])))

        validate_item = {'act': self.publish_type, 'validate': updates}
        validation_errors = get_resource_service('validate').post([validate_item])
        if validation_errors[0]:
            raise ValidationError(validation_errors)

    def on_updated(self, updates, original):
        self.update_published_collection(published_item=original)

    def update(self, id, updates, original):
        archived_item = super().find_one(req=None, _id=id)

        try:
            any_channel_closed = False

            if archived_item['type'] == 'composite':
                self.__publish_package_items(archived_item, updates[config.LAST_UPDATED])

            # document is saved to keep the initial changes
            set_sign_off(updates, original)
            self.backend.update(self.datasource, id, updates, original)

            # document is saved to change the status
            if (original.get('publish_schedule') or updates.get('publish_schedule')) \
                    and original[config.CONTENT_STATE] not in PUBLISH_STATES:
                updates[config.CONTENT_STATE] = 'scheduled'
            else:
                updates['publish_schedule'] = None
                updates[config.CONTENT_STATE] = self.published_state

            original.update(updates)
            get_component(ItemAutosave).clear(original['_id'])

            if archived_item['type'] != 'composite':
                # check if item is in a digital package
                package_id = TakesPackageService().get_take_package_id(original)
                if package_id:
                    # process the takes to form digital master file content
                    package, package_updates = self.process_takes(take=original, package_id=package_id)
                    package_updates[config.CONTENT_STATE] = self.published_state
                    resolve_document_version(document=package_updates,
                                             resource=ARCHIVE, method='PATCH',
                                             latest_doc=package)
                    self.backend.update(self.datasource, package['_id'], package_updates, package)
                    package.update(package_updates)
                    insert_into_versions(doc=package)

                    # send it to the digital channels
                    any_channel_closed_digital, queued_digital = \
                        self.publish(doc=package, target_output_channels=DIGITAL)

                    self.update_published_collection(published_item=package)
                else:
                    any_channel_closed_digital = False
                    queued_digital = False

                # queue only text items
                any_channel_closed_wire, queued_wire = \
                    self.publish(doc=original, target_output_channels=WIRE if package_id else None)

                any_channel_closed = any_channel_closed_digital or any_channel_closed_wire
                queued = queued_digital or queued_wire

                if not queued:
                    raise PublishQueueError.item_not_queued_error(Exception('Nothing is saved to publish queue'), None)

            self.backend.update(self.datasource, id, updates, original)
            user = get_user()
            push_notification('item:publish:closed:channels' if any_channel_closed else 'item:publish',
                              item=str(id), unique_name=archived_item['unique_name'],
                              desk=str(archived_item['task']['desk']),
                              user=str(user.get('_id', '')))
            original.update(super().find_one(req=None, _id=id))
        except SuperdeskApiError as e:
            raise e
        except KeyError as e:
            raise SuperdeskApiError.badRequestError(
                message="Key is missing on article to be published: {}"
                .format(str(e)))
        except Exception as e:
            logger.error("Something bad happened while publishing %s".format(id), e)
            raise SuperdeskApiError.internalError(message="Failed to publish the item: {}"
                                                  .format(str(e)))

    def publish(self, doc, target_output_channels=None):
        any_channel_closed, wrong_formatted_channels, queued = \
            self.queue_transmission(doc=doc, target_output_channels=target_output_channels)

        user = get_user()

        if wrong_formatted_channels and len(wrong_formatted_channels) > 0:
            push_notification('item:publish:wrong:format',
                              item=str(doc['_id']), unique_name=doc['unique_name'],
                              desk=str(doc['task']['desk']),
                              user=str(user.get('_id', '')),
                              output_channels=[c['name'] for c in wrong_formatted_channels])

        if not target_output_channels and not queued:
            raise PublishQueueError.item_not_queued_error(Exception('Nothing is saved to publish queue'), None)

        return any_channel_closed, queued

    def queue_transmission(self, doc, target_output_channels=None):
        try:
            if doc.get('destination_groups'):
                queued = False
                any_channel_closed = False
                wrong_formatted_channels = []

                destination_groups = self.resolve_destination_groups(
                    doc.get('destination_groups'))
                output_channels, selector_codes, format_types = \
                    self.resolve_output_channels(destination_groups.values())

                for output_channel in output_channels.values():
                    if target_output_channels == WIRE and output_channel.get('is_digital', False) or \
                            target_output_channels == DIGITAL and not output_channel.get('is_digital', False):
                        continue

                    if output_channel.get('is_active', True) is False:
                        any_channel_closed = True

                    subscribers = self.get_subscribers(output_channel)
                    if subscribers and subscribers.count() > 0:
                        formatter = get_formatter(output_channel['format'], doc['type'])
                        if not formatter:
                            # if formatter not found then record it
                            wrong_formatted_channels.append(output_channel)
                            continue

                        pub_seq_num, formatted_doc = formatter.format(doc, output_channel)

                        formatted_item = {'formatted_item': formatted_doc, 'format': output_channel['format'],
                                          'item_id': doc['_id'], 'item_version': doc.get('last_version', 0),
                                          'published_seq_num': pub_seq_num}

                        formatted_item_id = get_resource_service('formatted_item').post([formatted_item])[0]

                        publish_queue_items = []

                        for subscriber in subscribers:
                            for destination in subscriber.get('destinations', []):
                                publish_queue_item = dict()
                                publish_queue_item['item_id'] = doc['_id']
                                publish_queue_item['formatted_item_id'] = formatted_item_id
                                publish_queue_item['subscriber_id'] = subscriber['_id']
                                publish_queue_item['destination'] = destination
                                publish_queue_item['output_channel_id'] = output_channel['_id']
                                publish_queue_item['selector_codes'] = selector_codes.get(output_channel['_id'], [])
                                publish_queue_item['published_seq_num'] = pub_seq_num
                                publish_queue_item['publish_schedule'] = doc.get('publish_schedule', None)
                                publish_queue_item['publishing_action'] = doc.get(config.CONTENT_STATE, None)
                                publish_queue_item['unique_name'] = doc.get('unique_name', None)
                                publish_queue_item['content_type'] = doc.get('type', None)
                                publish_queue_item['headline'] = doc.get('headline', None)

                                publish_queue_items.append(publish_queue_item)

                        get_resource_service('publish_queue').post(publish_queue_items)
                        queued = True

                return any_channel_closed, wrong_formatted_channels, queued
            else:
                raise PublishQueueError.destination_group_not_found_error(
                    KeyError('Destination groups empty for article: {}'.format(doc['_id'])), None)
        except:
            raise

    def resolve_destination_groups(self, dg_ids, destination_groups=None):
        """
        This function flattens and returns the unique list of destination_groups
        :param dg_ids: initial list of destination group ids to be resolved and flatten
        :param destination_groups: dictionary of resolved id, destination_group
        :return: destination_groups
        """
        if destination_groups is None:
            destination_groups = {}

        lookup = {'_id': {'$in': dg_ids}}
        dgs = get_resource_service('destination_groups').get(req=None, lookup=lookup)
        for dg in dgs:
            if dg.get('destination_groups'):
                self.resolve_destination_groups(dg.get('destination_groups'), destination_groups)
            destination_groups[dg['_id']] = dg
        return destination_groups

    def resolve_output_channels(self, destination_groups):
        """
        This function returns the flattened list of output channels for a given unique
        list of destination groups
        :param destination_groups: unique list of destinations groups
        :return: output_channels:dictionary of resolved id, output_channel,
        lis of selector_codes, list of resolved format_types
        """
        output_channels = {}
        selector_codes = {}
        format_types = []
        for destination_group in destination_groups:
            if destination_group.get('output_channels'):
                selectors = []
                oc_ids = [oc['channel'] for oc in destination_group.get('output_channels', [])]
                lookup = {'_id': {'$in': oc_ids}}
                ocs = get_resource_service('output_channels').get(req=None, lookup=lookup)
                for oc in ocs:
                    output_channels[oc['_id']] = oc
                    format_types.append(oc['format'])
                    selectors = next((item.get('selector_codes', [])
                                      for item in destination_group.get('output_channels')
                                      if item['channel'] == oc['_id']), [])
                    selectors += selector_codes.get(oc['_id'], [])
                    selector_codes[oc['_id']] = list(set(selectors))

        return output_channels, selector_codes, list(set(format_types))

    def get_subscribers(self, output_channel):
        """
        Returns the list of subscribers for a given output channel
        :param output_channel: an output channel
        :return:list of subscribers
        """
        if output_channel.get('destinations'):
            subscriber_ids = output_channel['destinations']
            lookup = {'_id': {'$in': subscriber_ids}}
            return get_resource_service('subscribers').get(req=None, lookup=lookup)
        else:
            return None

    def __publish_package_items(self, package, last_updated):
        """
        Publishes items of a package recursively
        """

        items = [ref.get('residRef') for group in package.get('groups', [])
                 for ref in group.get('refs', []) if 'residRef' in ref]

        if items:
            for guid in items:
                doc = super().find_one(req=None, _id=guid)
                original = copy(doc)
                try:
                    if doc['type'] == 'composite':
                        self.__publish_package_items(doc)

                    resolve_document_version(document=doc, resource=ARCHIVE, method='PATCH', latest_doc=doc)
                    doc[config.CONTENT_STATE] = self.published_state
                    doc[config.LAST_UPDATED] = last_updated
                    doc[config.ETAG] = document_etag(doc)
                    self.backend.update(self.datasource, guid, {config.CONTENT_STATE: doc[config.CONTENT_STATE],
                                                                config.ETAG: doc[config.ETAG],
                                                                config.VERSION: doc[config.VERSION],
                                                                config.LAST_UPDATED: doc[config.LAST_UPDATED]},
                                        original)
                    insert_into_versions(doc=doc)
                except KeyError:
                    raise SuperdeskApiError.badRequestError("A non-existent content id is requested to publish")

    def process_takes(self, take, package_id):
        """
        This function validates if the take is the one in order then
        it generates the body_html of the takes package and make sure the
        metadata for the package is the same as the metadata of the take
        to be published
        :param take: The take to be published
        :return: It throws an error if the take is not the right take
        otherwise it returns the original package and the updated package
        """
        package = super().find_one(req=None, _id=package_id)
        package_updates = {}
        package_updates['body_html'] = ''
        take_index = 1000
        for group in package['groups']:
            if group['id'] == 'main':
                for i, ref in enumerate(group['refs']):
                    if ref['guid'] != take['_id']:
                        other_take = super().find_one(req=None, _id=ref['guid'])

                        if i < take_index:
                            # previous items
                            if other_take[config.CONTENT_STATE] not in ['published', 'corrected']:
                                # previous item is not published or killed
                                raise PublishQueueError.\
                                    previous_take_not_published_error(
                                        Exception('Take with id:{}'.format(other_take['_id'])), None)
                            else:
                                package_updates['body_html'] += other_take['body_html'] + '<br>'

                        if i > take_index:
                            # next takes
                            if other_take[config.CONTENT_STATE] in ['published', 'corrected']:
                                package_updates['body_html'] += other_take['body_html'] + '<br>'
                            if other_take[config.CONTENT_STATE] in ['killed']:
                                raise PublishQueueError.\
                                    previous_take_not_published_error(
                                        Exception('Take with id:{}'.format(other_take['_id'])), None)

                    else:
                        take_index = i
                        package_updates['body_html'] += take['body_html'] + '<br>'
                        self.update_metadata(take, package_updates)
        return package, package_updates

    def update_metadata(self, take, package):
        metadata_tobe_copied = ['headline',
                                'abstract',
                                'anpa-category',
                                'pubstatus',
                                'destination_groups',
                                'slugline',
                                'urgency',
                                'subject'
                                ]

        for metadata in metadata_tobe_copied:
            package[metadata] = take[metadata]

    def update_published_collection(self, published_item):
        get_resource_service('published').update_published_items(published_item['_id'],
                                                                 'last_publish_action',
                                                                 self.published_state)
        get_resource_service('published').post([copy(published_item)])


class ArchivePublishResource(BasePublishResource):

    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'publish')


class ArchivePublishService(BasePublishService):
    publish_type = 'publish'
    published_state = 'published'


class KillPublishResource(BasePublishResource):

    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'kill')


class KillPublishService(BasePublishService):
    publish_type = 'kill'
    published_state = 'killed'


class CorrectPublishResource(BasePublishResource):

    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'correct')


class CorrectPublishService(BasePublishService):
    publish_type = 'correct'
    published_state = 'corrected'


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
