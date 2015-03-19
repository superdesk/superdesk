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

from eve.versioning import resolve_document_version
from flask import current_app as app
from eve.utils import config, document_etag
from copy import copy
from apps.archive.common import item_url, get_user, insert_into_versions
from superdesk.errors import InvalidStateTransitionError, SuperdeskApiError
from superdesk.notification import push_notification
from superdesk.services import BaseService
import superdesk
from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from superdesk.workflow import is_workflow_state_transition_valid


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
            user = get_user()
            updates[config.CONTENT_STATE] = 'published'
            item = self.backend.update(self.datasource, id, updates, original)
            push_notification('item:publish', item=str(item.get('_id')), user=str(user))
            return item
        except KeyError:
            raise SuperdeskApiError.badRequestError(message="A non-existent content id is requested to publish")
        except Exception as e:
            logger.error("Something bad happened while publishing %s".format(id), e)
            raise SuperdeskApiError.internalError(message="Failed to publish the item")

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
