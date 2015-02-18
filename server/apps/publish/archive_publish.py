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

from flask import current_app as app
from eve.utils import config

from apps.archive.common import item_url, get_user
from superdesk.errors import InvalidStateTransitionError
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

    def update(self, id, updates):

        updates[config.CONTENT_STATE] = 'published'
        user = get_user(required=True)

        item = self.backend.update(self.datasource, id, updates)

        push_notification('item:publish', item=str(item.get('_id')), user=str(user))

        return item


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
