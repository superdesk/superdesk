# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.resource import Resource
from .common import item_url
from superdesk.services import BaseService
import superdesk
import logging

logger = logging.getLogger(__name__)


class ArchivePublishResource(Resource):
    endpoint_name = 'archive_publish'
    url = 'archive/<{0}:item_id>/publish'.format(item_url)
    datasource = {'source': 'archive'}
    resource_methods = ['POST', 'DELETE', 'PATCH']
    resource_title = endpoint_name
    privileges = {'POST': 'publish', 'DELETE': 'kill', 'PATCH': 'correction'}


class ArchivePublishService(BaseService):
    pass


superdesk.workflow_state('published')
superdesk.workflow_state('killed')
superdesk.workflow_state('corrected')


superdesk.workflow_action(
    name='publish',
    include_states=['draft'],
    privileges=['publish']
)

superdesk.workflow_action(
    name='kill',
    include_states=['published'],
    privileges=['kill']
)

superdesk.workflow_action(
    name='correct',
    include_states=['published'],
    privileges=['correction']
)
