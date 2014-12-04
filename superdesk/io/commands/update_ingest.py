import logging
import superdesk
from superdesk.notification import push_notification
from superdesk.io import providers
from superdesk.celery_app import celery
from eve.utils import config
from superdesk.utc import utcnow
from datetime import timedelta
from flask import current_app as app
from werkzeug.exceptions import HTTPException


UPDATE_SCHEDULE_DEFAULT = {'minutes': 5}
LAST_UPDATED = 'last_updated'

logger = logging.getLogger(__name__)


def is_valid_type(provider, provider_type_filter=None):
    """Test if given provider has valid type and should be updated.

    :param provider: provider to be updated
    :param provider_type_filter: active provider type filter
    """
    provider_type = provider.get('type')
    if provider_type not in providers:
        return False
    if provider_type_filter and provider_type != provider_type_filter:
        return False
    return True


def is_scheduled(provider):
    """Test if given provider should be scheduled for update.

    :param provider: ingest provider
    """
    now = utcnow()
    last_updated = provider.get(LAST_UPDATED, now - timedelta(days=100))  # if never updated run now
    update_schedule = provider.get('update_schedule', UPDATE_SCHEDULE_DEFAULT)
    return last_updated + timedelta(**update_schedule) < now


def is_closed(provider):
    """Test if provider is closed.

    :param provider: ingest provider
    """
    return provider.get('is_closed', False)


class UpdateIngest(superdesk.Command):
    """Update ingest providers."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in superdesk.get_resource_service('ingest_providers').get(req=None, lookup={}):
            if is_valid_type(provider, provider_type) and is_scheduled(provider) and not is_closed(provider):
                update_provider.delay(str(provider['_id']))


@celery.task
def update_provider(provider_id):
    """Update provider by given id."""
    last_updated = utcnow()
    provider = superdesk.get_resource_service('ingest_providers').find_one(req=None, _id=provider_id)
    superdesk.get_resource_service('ingest_providers').update(provider['_id'], {
        LAST_UPDATED: last_updated,
        app.config['ETAG']: provider.get(app.config['ETAG']),  # keep the etag
    })
    for items in providers[provider.get('type')].update(provider):
        ingest_items(provider, items)
    push_notification('ingest:update')


def process_anpa_category(item):
    anpa_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')
    if anpa_categories:
        for anpa_category in anpa_categories['items']:
            if anpa_category['is_active'] is True \
                    and item['anpa-category']['qcode'].lower() == anpa_category['value'].lower():
                item['anpa-category'] = {'qcode': item['anpa-category']['qcode'], 'name': anpa_category['name']}
                break


def ingest_items(provider, items):
    for item in items:
        item.setdefault('_id', item['guid'])

        item['ingest_provider'] = str(provider['_id'])
        item.setdefault('source', provider.get('source', ''))

        if 'anpa-category' in item:
            process_anpa_category(item)

        old_item = superdesk.get_resource_service('ingest').find_one(_id=item['guid'], req=None)
        if old_item:
            superdesk.get_resource_service('ingest').put(item['guid'], item)
        else:
            item[config.VERSION] = 1
            try:
                superdesk.get_resource_service('ingest').post([item])
            except HTTPException:
                # there was a conflict in mongo
                pass


superdesk.command('ingest:update', UpdateIngest())
