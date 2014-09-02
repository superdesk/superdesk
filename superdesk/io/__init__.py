"""Superdesk IO"""

import logging
import superdesk
from superdesk.utc import utcnow
from superdesk.base_model import BaseModel
from flask import current_app as app
from superdesk.celery_app import celery
from superdesk.notification import push_notification


logger = logging.getLogger(__name__)
providers = {}


def register_provider(type, provider):
    providers[type] = provider

superdesk.provider = register_provider


def update_provider(provider):
    """Update given provider."""
    if provider.get('type') in providers:
        for items in providers[provider.get('type')].update(provider):
            ingest_items(provider, items)


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
                app.data.update('ingest', str(old_item.get('_id')), item)
            else:
                ingested_count += 1
                app.data.insert('ingest', [item])

        app.data.update('ingest_providers', provider['_id'], {
            '_updated': start,
            'ingested_count': ingested_count
        })


@celery.task()
def fetch_ingest():
    UpdateIngest().run()


class UpdateIngest(superdesk.Command):
    """Update ingest providers."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in app.data.find_all('ingest_providers'):
            if not provider_type or provider_type == provider.get('type'):
                try:
                    update_provider(provider)
                except (Exception) as err:
                    logger.exception(err)
                    pass
                finally:
                    push_notification('ingest:update')


class AddProvider(superdesk.Command):
    """Add ingest provider."""

    option_list = {
        superdesk.Option('--provider', '-p', dest='provider'),
    }

    def run(self, provider=None):
        if provider:
            data = superdesk.json.loads(provider)
            data.setdefault('_created', utcnow())
            data.setdefault('_updated', utcnow())
            data.setdefault('name', data['type'])
            db = superdesk.get_db()
            db['ingest_providers'].save(data)
            return data

superdesk.command('ingest:update', UpdateIngest())
superdesk.command('ingest:provider', AddProvider())

# load providers now to have available types for the schema
import superdesk.io.reuters
import superdesk.io.aap


def init_app(app):
    IngestProviderModel(app=app)


class IngestProviderModel(BaseModel):
    schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'type': {
            'type': 'string',
            'required': True,
            'allowed': providers.keys()
        },
        'config': {
            'type': 'dict'
        },
        'ingested_count': {
            'type': 'integer'
        },
        'accepted_count': {
            'type': 'integer'
        },
        'token': {
            'type': 'dict'
        }
    }

    endpoint_name = 'ingest_providers'
