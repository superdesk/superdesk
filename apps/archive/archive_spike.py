import logging

from eve.versioning import resolve_document_version, insert_versioning_documents
from flask import request, current_app as app
from eve.utils import ParsedRequest, date_to_str

from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from superdesk import get_resource_service
from superdesk.notification import push_notification
from .common import get_user, item_url
from superdesk.services import BaseService
from apps.item_lock.components.item_spike import get_unspike_updates
import superdesk
from superdesk.utc import utcnow, get_expiry_date


logger = logging.getLogger(__name__)


class ArchiveSpikeResource(ArchiveResource):
    endpoint_name = 'archive_spike'
    resource_title = endpoint_name
    datasource = {'source': ARCHIVE}

    url = "archive/spike"
    item_url = item_url

    resource_methods = []
    item_methods = ['PATCH', 'DELETE']

    privileges = {'PATCH': 'spike', 'DELETE': 'unspike'}


EXPIRY = 'expiry'
REVERT_STATE = 'revert_state'


class ArchiveSpikeService(BaseService):

    def update(self, id, updates):
        user = get_user(required=True)

        item = get_resource_service(ARCHIVE).find_one(req=None, _id=id)
        expiry_minutes = app.settings['SPIKE_EXPIRY_MINUTES']

        # check if item is in a desk. If it's then use the desks spike_expiry
        if 'task' in item and 'desk' in item['task']:
            desk = get_resource_service('desks').find_one(_id=item['task']['desk'], req=None)
            expiry_minutes = desk.get('spike_expiry', expiry_minutes)

        updates[EXPIRY] = get_expiry_date(expiry_minutes)
        updates[REVERT_STATE] = item.get(app.config['CONTENT_STATE'], None)

        item = self.backend.update(self.datasource, id, updates)
        push_notification('item:spike', item=str(item.get('_id')), user=str(user))

        # build_custom_hateoas(custom_hateoas, item)
        return item

    def delete(self, lookup):
        user = get_user(required=True)
        item_id = request.view_args['_id']

        item = get_resource_service(ARCHIVE).find_one(req=None, _id=item_id)
        updates = get_unspike_updates(item)
        resolve_document_version(updates, ARCHIVE, 'DELETE', item)
        self.backend.update(self.datasource, item_id, updates)

        item = get_resource_service(ARCHIVE).find_one(req=None, _id=item_id)
        insert_versioning_documents(ARCHIVE, item)
        push_notification('item:unspike', item=str(filter.get('_id')), user=str(user))


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
                     {'term': {'state': 'spiked'}},
                     {'range': {'expiry': {'lte': now}}},
                 ]
                 }
        return superdesk.json.dumps(query)

superdesk.command('archive:spike', ArchiveRemoveExpiredSpikes())

superdesk.workflow_state('spiked')

superdesk.workflow_action(
    name='spike',
    exclude_states=['spiked', 'published', 'killed'],
    privileges=['spike'],
)

superdesk.workflow_action(
    name='unspike',
    include_states=['spiked'],
    privileges=['unspike']
)
