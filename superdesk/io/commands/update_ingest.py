import logging
import superdesk
from superdesk.utc import utcnow
from flask import current_app as app
from superdesk.notification import push_notification
from superdesk.io import providers
from superdesk.celery_app import celery

logger = logging.getLogger(__name__)


class UpdateIngest(superdesk.Command):
    """Update ingest providers."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in app.data.find_all('ingest_providers'):
            if not provider_type or provider_type == provider.get('type'):
                try:
                    update_provider.delay(provider)
                except (Exception) as err:
                    logger.exception(err)
                    pass

superdesk.command('ingest:update', UpdateIngest())


@celery.task
def update_provider(provider):
    """Update given provider."""
    if provider.get('type') in providers:
        for items in providers[provider.get('type')].update(provider):
            ingest_items(provider, items)
    push_notification('ingest:update')


def ingest_items(provider, items):
        start = utcnow()
        ingested_count = provider.get('ingested_count', 0)
        for item in items:
            item.setdefault('_id', item['guid'])
            item.setdefault('_created', utcnow())
            item.setdefault('_updated', utcnow())
            item['ingest_provider'] = str(provider['_id'])
            old_item = app.data.find_one('ingest', guid=item['guid'], req=None)
            if old_item:
                app.data.replace('ingest', item['guid'], item)
            else:
                ingested_count += 1
                app.data.insert('ingest', [item])

        app.data.update('ingest_providers', provider['_id'], {
            '_updated': start,
            'ingested_count': ingested_count
        })
