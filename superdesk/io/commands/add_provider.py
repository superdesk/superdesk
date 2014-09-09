import superdesk
from superdesk.utc import utcnow
from superdesk.io.ingest_provider_model import DAYS_TO_KEEP


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
            data.setdefault('days_to_keep', DAYS_TO_KEEP)
            db = superdesk.get_db()
            db['ingest_providers'].save(data)
            return data


superdesk.command('ingest:provider', AddProvider())
