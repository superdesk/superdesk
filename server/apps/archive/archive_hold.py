# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import request
from superdesk.resource import Resource, build_custom_hateoas
from .common import get_user, get_auth, CUSTOM_HATEOAS
from superdesk.metadata.utils import item_url
from superdesk.services import BaseService
from apps.common.components.utils import get_component
from apps.item_lock.components.item_hold import ItemHold
import superdesk
import logging

logger = logging.getLogger(__name__)


class ArchiveHoldResource(Resource):
    endpoint_name = 'archive_hold'
    url = 'archive/<{0}:item_id>/hold'.format(item_url)
    datasource = {'source': 'archive'}
    resource_methods = ['POST', 'DELETE']
    resource_title = endpoint_name
    privileges = {'POST': 'hold', 'DELETE': 'restore'}


class ArchiveHoldService(BaseService):

    def create(self, docs, **kwargs):
        user = get_user(required=True)
        auth = get_auth()
        item_id = request.view_args['item_id']
        item = get_component(ItemHold).hold({'_id': item_id}, user['_id'], auth['_id'])
        build_custom_hateoas(CUSTOM_HATEOAS, item)
        return [item['_id']]

    def delete(self, lookup):
        user = get_user(required=True)
        item_id = request.view_args['item_id']
        get_component(ItemHold).restore({'_id': item_id}, user['_id'])


superdesk.workflow_state('on_hold')

superdesk.workflow_action(
    name='hold',
    exclude_states=['ingested', 'draft', 'spiked', 'published', 'killed'],
    privileges=['hold']
)

superdesk.workflow_action(
    name='restore',
    include_states=['on_hold'],
    privileges=['restore']
)
