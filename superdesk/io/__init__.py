"""Superdesk IO"""

import superdesk
from superdesk.utc import utcnow
from superdesk.base_view_controller import BaseViewController
from flask import current_app as app

providers = {}


def register_provider(type, provider):
    providers[type] = provider

superdesk.provider = register_provider


def update_provider(provider):
    """Update given provider."""

    if provider.get('type') in providers:
        start = utcnow()
        ingested_count = provider.get('ingested_count', 0)
        for item in providers[provider.get('type')].update(provider):
            item.setdefault('created', utcnow())
            item.setdefault('updated', utcnow())
            item['ingest_provider'] = str(provider['_id'])

            old_item = app.data.find_one('ingest', guid=item['guid'], req=None)
            if old_item:
                app.data.update('ingest', str(old_item.get('_id')), item)
            else:
                ingested_count += 1
                app.data.insert('ingest', [item], ttl='7d')

        app.data.update('ingest_providers', provider['_id'], {
            'updated': start,
            'ingested_count': ingested_count
        })


class UpdateIngest(superdesk.Command):
    """Update ingest providers."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in app.data.find_all('ingest_providers'):
            if not provider_type or provider_type == provider.get('type'):
                update_provider(provider)


class AddProvider(superdesk.Command):
    """Add ingest provider."""

    option_list = {
        superdesk.Option('--provider', '-p', dest='provider'),
    }

    def run(self, provider=None):
        if provider:
            data = superdesk.json.loads(provider)
            data.setdefault('created', utcnow())
            data.setdefault('updated', utcnow())
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
    IngestProviderViewController(app=app)


class IngestProviderViewController(BaseViewController):
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
