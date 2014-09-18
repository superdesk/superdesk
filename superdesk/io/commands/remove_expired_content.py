import logging
import superdesk
from eve.utils import ParsedRequest, date_to_str
from datetime import timedelta
from superdesk.utc import utcnow
from flask import current_app as app
from superdesk.notification import push_notification
from superdesk.io.ingest_provider_model import DAYS_TO_KEEP

logger = logging.getLogger(__name__)


class RemoveExpiredContent(superdesk.Command):
    """Remove stale data from ingest based on the provider settings."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in app.data.find_all('ingest_providers'):
            if not provider_type or provider_type == provider.get('type'):
                try:
                    remove_expired_data(provider)
                except (Exception) as err:
                    logger.exception(err)
                    pass
                finally:
                    push_notification('ingest:cleaned')


superdesk.command('ingest:clean_expired', RemoveExpiredContent())


def remove_expired_data(provider):
    """Remove expired data for provider"""
    print('Removing expired content for provider: %s' % provider['_id'])
    days_to_keep_content = provider.get('days_to_keep', DAYS_TO_KEEP)
    expiration_date = utcnow() - timedelta(days=days_to_keep_content)

    items = get_expired_items(str(provider['_id']), expiration_date)
    while items.count() > 0:
        for item in items:
            print('Removing item %s' % item['_id'])
            app.data.remove('ingest', {'_id': str(item['_id'])})

        items = get_expired_items(str(provider['_id']), expiration_date)

    print('Removed expired content for provider: %s' % provider['_id'])


def get_expired_items(provider_id, expiration_date):
    query_filter = get_query_for_expired_items(provider_id, expiration_date)
    req = ParsedRequest()
    req.max_results = 100
    req.args = {'filter': query_filter}
    return app.data.find('ingest', req, None)


def get_query_for_expired_items(provider_id, expiration_date):
    query = {'bool':
             {
                 'must': [
                     {
                         'range': {'ingest._updated': {'lte': date_to_str(expiration_date)}}
                     },
                     {
                         'term': {'ingest.ingest_provider': provider_id}
                     }
                 ]
             }
             }
    return superdesk.json.dumps(query)
