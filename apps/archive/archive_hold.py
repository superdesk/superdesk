from flask import request
from superdesk.resource import Resource, build_custom_hateoas
from .common import get_user, item_url
from .archive_lock import custom_hateoas
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
        item_id = request.view_args['item_id']
        item = get_component(ItemHold).hold({'_id': item_id}, user['_id'])
        build_custom_hateoas(custom_hateoas, item)
        return [item['_id']]

    def delete(self, lookup):
        user = get_user(required=True)
        item_id = request.view_args['item_id']
        get_component(ItemHold).restore({'_id': item_id}, user['_id'])


superdesk.workflow_state('on-hold')

superdesk.workflow_action(
    name='hold',
    exclude_states=['ingested', 'draft', 'spiked', 'published', 'killed'],
    privileges=['hold']
)

superdesk.workflow_action(
    name='restore',
    include_states=['on-hold'],
    privileges=['restore']
)
