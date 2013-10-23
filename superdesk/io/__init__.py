"""Superdesk IO"""

import superdesk
from superdesk.utc import utcnow

providers = {}

def register_provider(type, provider):
    providers[type] = provider

def update_provider(provider, db):
    """Update given provider."""

    if provider.get('type') in providers:
        start = utcnow()
        ingested_count = 0
        for item in providers[provider.get('type')].update(provider):
            item.setdefault('created', utcnow())
            item.setdefault('updated', utcnow())
            item['ingest_provider'] = provider['_id']

            old_item = db['items'].find_one({'guid': item['guid']})
            if old_item:
                db['items'].remove(old_item)

            db['items'].save(item)
            provider['ingested_count'] = provider.get('ingested_count', 0) + 1
        provider['updated'] = start
        db['ingest_providers'].save(provider)

class UpdateIngest(superdesk.Command):
    """Update ingest feeds."""

    def run(self):
        db = superdesk.get_db()
        for provider in db['ingest_providers'].find():
            update_provider(provider, db)

superdesk.command('ingest:update', UpdateIngest())

superdesk.domain('feeds', {
    'schema': {
        'provider': {
            'type': 'string'
        }
    }
})

# load providers now to have available types for the schema
import superdesk.io.reuters

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
        'type': 'integer',
        'readonly': True
    },
    'accepted_count': {
        'type': 'integer',
        'readonly': True
    }
}

superdesk.domain('ingest_providers', {
    'schema': schema
})
