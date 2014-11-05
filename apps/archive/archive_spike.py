from flask import request
from superdesk.resource import Resource, build_custom_hateoas
from .common import get_user, item_url
from .archive_lock import custom_hateoas
from superdesk.services import BaseService
from apps.common.components.utils import get_component
from apps.item_lock.components.item_spike import ItemSpike


class ArchiveSpikeResource(Resource):
    endpoint_name = 'archive_spike'
    url = 'archive/<{0}:item_id>/spike'.format(item_url)
    schema = {'is_spiked': {'type': 'boolean'}}
    datasource = {'source': 'archive'}
    resource_methods = ['POST', 'DELETE']
    resource_title = endpoint_name


class ArchiveSpikeService(BaseService):

    def create(self, docs, **kwargs):
        user = get_user(required=True)
        item_id = request.view_args['item_id']
        item = get_component(ItemSpike).spike({'_id': item_id}, user['_id'])
        build_custom_hateoas(custom_hateoas, item)
        return [item['_id']]

    def delete(self, lookup):
        user = get_user(required=True)
        item_id = request.view_args['item_id']
        get_component(ItemSpike).unspike({'_id': item_id}, user['_id'])
