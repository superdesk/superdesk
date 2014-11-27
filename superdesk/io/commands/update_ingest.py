from _datetime import datetime
import logging
import superdesk
from superdesk.notification import push_notification
from superdesk.io import providers
from superdesk.celery_app import celery
from eve.utils import config

logger = logging.getLogger(__name__)


class UpdateIngest(superdesk.Command):
    """Update ingest providers."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in superdesk.get_resource_service('ingest_providers').get(req=None, lookup={}):
            if not provider_type or provider_type == provider.get('type'):
                try:
                    update_provider.delay(provider)
                except Exception as err:
                    logger.exception(err)

superdesk.command('ingest:update', UpdateIngest())


@celery.task
def update_provider(provider):
    """Update given provider."""
    if provider.get('type') in providers:
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
        ingested_count = provider.get('ingested_count', 0)

        # TODO: Hate to do this but there is no alternative, might be a bug in Pymongo
        if isinstance(ingested_count, datetime):
            ingested_count = 0

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
                ingested_count += 1
                item[config.VERSION] = 1
                superdesk.get_resource_service('ingest').post([item])

        superdesk.get_resource_service('ingest_providers').patch(provider['_id'], {
            'ingested_count': ingested_count
        })
        return ingested_count
