# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import logging
import superdesk

from eve.versioning import resolve_document_version
from flask import current_app as app
from eve.utils import config, document_etag
from copy import copy
from apps.archive.common import item_url, get_user, insert_into_versions
from superdesk.errors import InvalidStateTransitionError, SuperdeskApiError, PublishQueueError
from superdesk.notification import push_notification
from superdesk.services import BaseService
from superdesk import get_resource_service
from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from superdesk.workflow import is_workflow_state_transition_valid
from apps.publish.formatters import get_formatter


logger = logging.getLogger(__name__)


class ArchivePublishResource(ArchiveResource):
    """
    Resource class for "publish" endpoint.
    """

    endpoint_name = 'archive_publish'
    resource_title = endpoint_name
    datasource = {'source': ARCHIVE}

    url = "archive/publish"
    item_url = item_url

    resource_methods = []
    item_methods = ['PATCH']

    privileges = {'PATCH': 'publish'}


class ArchivePublishService(BaseService):
    """
    Service class for "publish" endpoint
    """

    def on_update(self, updates, original):
        if not is_workflow_state_transition_valid('publish', original[app.config['CONTENT_STATE']]):
            raise InvalidStateTransitionError()

    def update(self, id, updates, original):
        archived_item = super().find_one(req=None, _id=id)
        try:
            if archived_item['type'] == 'composite':
                self.__publish_package_items(archived_item, updates[config.LAST_UPDATED])

            # document is saved to keep the initial changes
            self.backend.update(self.datasource, id, updates, original)
            original.update(updates)

            if archived_item['type'] != 'composite':
                # queue only text items
                self.queue_transmission(original)
                task = self.__send_to_publish_stage(original)
                if task:
                    updates['task'] = task

            # document is saved to change the status
            updates[config.CONTENT_STATE] = 'published'
            item = self.backend.update(self.datasource, id, updates, original)
            original.update(updates)
            user = get_user()
            push_notification('item:publish', item=str(item.get('_id')), user=str(user))
            original.update(super().find_one(req=None, _id=id))
        except KeyError as e:
            raise SuperdeskApiError.badRequestError(
                message="Key is missing on article to be published: {}"
                .format(str(e)))
        except Exception as e:
            logger.error("Something bad happened while publishing %s".format(id), e)
            raise SuperdeskApiError.internalError(message="Failed to publish the item: {}"
                                                  .format(str(e)))

    def queue_transmission(self, doc):
        try:
            if doc.get('destination_groups'):
                destination_groups = self.resolve_destination_groups(doc.get('destination_groups'))
                output_channels, selector_codes, format_types = \
                    self.resolve_output_channels(destination_groups.values())

                for output_channel in output_channels.values():
                    subscribers = self.get_subscribers(output_channel)
                    if subscribers.count() > 0:
                        formatter = get_formatter(output_channel['format'])

                        formatted_item = {}
                        formatted_item['formatted_item'] = formatter.format(doc, output_channel)
                        formatted_item['format'] = output_channel['format']
                        formatted_item['item_id'] = doc['_id']
                        formatted_item['item_version'] = doc.get('last_version', 0)
                        formatted_item_id = get_resource_service('formatted_item').post([formatted_item])[0]

                        publish_queue_items = []

                        for subscriber in subscribers:
                            for destination in subscriber.get('destinations', []):
                                publish_queue_item = {}
                                publish_queue_item['item_id'] = doc['_id']
                                publish_queue_item['formatted_item_id'] = formatted_item_id
                                publish_queue_item['subscriber_id'] = subscriber['_id']
                                publish_queue_item['destination'] = destination
                                publish_queue_item['output_channel_id'] = output_channel['_id']
                                publish_queue_item['selector_codes'] = selector_codes.get(output_channel['_id'], [])

                                publish_queue_items.append(publish_queue_item)

                        get_resource_service('publish_queue').post(publish_queue_items)
            else:
                raise PublishQueueError.destination_group_not_found_error(
                    KeyError('Destination groups empty for article: {}'.format(doc['_id'])), None)
        except:
            raise

    def resolve_destination_groups(self, dg_ids, destination_groups=None):
        '''
        This function flattens and returns the unique list of destination_groups
        :param dg_ids: initial list of destination group ids to be resolved and flatten
        :param destination_groups: dictionary of resolved id, destination_group
        :return: destination_groups
        '''
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
        '''
        This function returns the flattened list of output channels for a given unique
        list of destination groups
        :param destination_groups: unique list of destinations groups
        :return: output_channels:dictionary of resolved id, output_channel,
        lis of selector_codes, list of resolved format_types
        '''
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
        '''
        Returns the list of subscribers for a given output channel
        :param output_channel: an output channel
        :return:list of subscribers
        '''
        if output_channel.get('destinations'):
            subscriber_ids = output_channel['destinations']
            lookup = {'_id': {'$in': subscriber_ids}}
            return get_resource_service('subscribers').get(req=None, lookup=lookup)
        else:
            return None

    def __publish_package_items(self, package, last_updated):
        """
        Publishes items of a package recursively

        :return: True if all the items of a package have been published successfully. False otherwise.
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
                    doc[config.CONTENT_STATE] = 'published'
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

    def __send_to_publish_stage(self, doc):
        desk = get_resource_service('desks').find_one(req=None, _id=doc['task']['desk'])
        if desk.get('published_stage') and doc['task']['stage'] != desk['published_stage']:
            doc['task']['stage'] = desk['published_stage']
            return get_resource_service('move').move_content(doc['_id'], doc)['task']


superdesk.workflow_state('published')
superdesk.workflow_action(
    name='publish',
    include_states=['fetched', 'routed', 'submitted', 'in_progress'],
    privileges=['publish']
)

superdesk.workflow_state('killed')
superdesk.workflow_action(
    name='kill',
    include_states=['published'],
    privileges=['kill']
)

superdesk.workflow_state('corrected')
superdesk.workflow_action(
    name='correct',
    include_states=['published'],
    privileges=['correction']
)
