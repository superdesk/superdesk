from flask import request
from superdesk.resource import Resource, build_custom_hateoas
from .common import get_user, item_url
from .archive_lock import custom_hateoas
from superdesk.services import BaseService
from apps.common.components.utils import get_component
from apps.item_lock.components.item_spike import ItemSpike
import superdesk
from eve.utils import ParsedRequest, date_to_str
from superdesk.utc import utcnow
from eve.versioning import insert_versioning_documents
import logging

logger = logging.getLogger(__name__)


class ArchiveSpikeResource(Resource):
    endpoint_name = 'archive_spike'
    url = 'archive/<{0}:item_id>/spike'.format(item_url)
    # we may need to re-visit this field as it is redundant now
    # but we still need the expiry field for spiked items
    schema = {'is_spiked': {'type': 'boolean'}}
    datasource = {'source': 'archive'}
    resource_methods = ['POST', 'DELETE']
    resource_title = endpoint_name
    privileges = {'POST': 'spike', 'DELETE': 'unspike'}


class ArchiveSpikeService(BaseService):

    def create(self, docs, **kwargs):
        user = get_user(required=True)
        item_id = request.view_args['item_id']
        item = get_component(ItemSpike).spike({'_id': item_id}, user['_id'])
        self.increment_version(item_id)
        build_custom_hateoas(custom_hateoas, item)
        return [item['_id']]

    def delete(self, lookup):
        user = get_user(required=True)
        item_id = request.view_args['item_id']
        get_component(ItemSpike).unspike({'_id': item_id}, user['_id'])
        self.increment_version(item_id)

    def increment_version(self, id):
        doc = superdesk.get_resource_service('archive').find_one(req=None, _id=id)
        insert_versioning_documents('archive', doc)


class ArchiveRemoveExpiredSpikes(superdesk.Command):

    def run(self):
        self.remove_expired_spiked()

    def remove_expired_spiked(self):
        logger.info('Expiring spiked content')
        now = date_to_str(utcnow())
        items = self.get_expired_items(now)
        while items.count() > 0:
            for item in items:
                logger.info('deleting {} expiry: {} now:{}'.format(item['_id'], item['expiry'], now))
                superdesk.get_resource_service('archive').delete_action({'_id': str(item['_id'])})
            items = self.get_expired_items(now)

    def get_expired_items(self, now):
        query_filter = self.get_query_for_expired_items(now)
        req = ParsedRequest()
        req.max_results = 100
        req.args = {'filter': query_filter}
        return superdesk.get_resource_service('archive').get(req, None)

    def get_query_for_expired_items(self, now):
        query = {'and':
                 [
                     {'term': {'is_spiked': True}},
                     {'range': {'expiry': {'lte': now}}},
                 ]
                 }
        return superdesk.json.dumps(query)

superdesk.command('archive:spike', ArchiveRemoveExpiredSpikes())

superdesk.workflow_state('spiked')

superdesk.workflow_action(
    name='spike',
    exclude_states=['spiked', 'published', 'killed'],
    privileges=['spike']
)

superdesk.workflow_action(
    name='unspike',
    include_states=['spiked'],
    privileges=['unspike']
)
