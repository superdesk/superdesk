import logging

from flask import current_app as app
from eve.utils import ParsedRequest, date_to_str

from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from superdesk import get_resource_service
from superdesk.notification import push_notification
from .common import get_user, item_url
from superdesk.services import BaseService
import superdesk
from superdesk.utc import utcnow, get_expiry_date


logger = logging.getLogger(__name__)


EXPIRY = 'expiry'
REVERT_STATE = 'revert_state'


class ArchiveSpikeResource(ArchiveResource):
    endpoint_name = 'archive_spike'
    resource_title = endpoint_name
    datasource = {'source': ARCHIVE}

    url = "archive/spike"
    item_url = item_url

    resource_methods = []
    item_methods = ['PATCH']

    privileges = {'PATCH': 'spike'}


class ArchiveUnspikeResource(ArchiveResource):
    endpoint_name = 'archive_unspike'
    resource_title = endpoint_name
    datasource = {'source': ARCHIVE}

    url = "archive/unspike"
    item_url = item_url

    resource_methods = []
    item_methods = ['PATCH']

    privileges = {'PATCH': 'unspike'}


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


class ArchiveUnspikeService(BaseService):

    def get_unspike_updates(self, doc):
        """Generate changes for a given doc to unspike it.

        :param doc: document to unspike
        """
        updates = {REVERT_STATE: None, EXPIRY: None, 'state': doc.get(REVERT_STATE)}

        desk_id = doc.get('task', {}).get('desk')
        if desk_id:
            desk = app.data.find_one('desks', None, _id=desk_id)
            updates['task'] = {
                'desk': str(desk_id),
                'stage': str(desk['incoming_stage']) if desk_id else None,
                'user': None
            }

        return updates

    def update(self, id, updates):
        user = get_user(required=True)

        item = get_resource_service(ARCHIVE).find_one(req=None, _id=id)
        updates.update(self.get_unspike_updates(item))

        self.backend.update(self.datasource, id, updates)
        item = get_resource_service(ARCHIVE).find_one(req=None, _id=id)

        push_notification('item:unspike', item=str(id), user=str(user))
        return item


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
