import logging
import superdesk
from eve.utils import ParsedRequest, date_to_str
from datetime import timedelta
from superdesk.utc import utcnow
from superdesk.notification import push_notification
from superdesk.io.ingest_provider_model import DAYS_TO_KEEP
from flask import current_app as app


logger = logging.getLogger(__name__)


class RemoveExpiredContent(superdesk.Command):
    """Remove stale data from ingest based on the provider settings."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        try:
            remove_expired_sessions()
        except (Exception) as err:
            logger.exception(err)

        for provider in superdesk.get_resource_service('ingest_providers').get(req=None, lookup={}):
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
            superdesk.get_resource_service('ingest').delete_action({'_id': str(item['_id'])})

        items = get_expired_items(str(provider['_id']), expiration_date)

    print('Removed expired content for provider: %s' % provider['_id'])


def get_expired_items(provider_id, expiration_date):
    query_filter = get_query_for_expired_items(provider_id, expiration_date)
    req = ParsedRequest()
    req.max_results = 100
    req.args = {'filter': query_filter}
    return superdesk.get_resource_service('ingest').get(req, None)


def get_query_for_expired_items(provider_id, expiration_date):
    query = {'and':
             [
                 {'term': {'ingest.ingest_provider': provider_id}},
                 {'range': {'ingest.versioncreated': {'lte': date_to_str(expiration_date)}}},
             ]
             }
    return superdesk.json.dumps(query)


def remove_expired_sessions():
    sessions = get_expired_sessions()
    for session in sessions:
        print('Deleting session {0} created {1} by {2}'.format(session['_id'],
                                                               session['_updated'], session['username']))
        superdesk.get_resource_service('auth').delete_action({'_id': str(session['_id'])})


def get_expired_sessions():
    expiry_minutes = app.settings['SESSION_EXPIRY_MINUTES']
    expiration_time = utcnow() - timedelta(minutes=expiry_minutes)
    print('Deleting session not updated since {}'.format(expiration_time))
    query_filter = get_query_for_expired_sessions(expiration_time)
    req = ParsedRequest()
    req.max_results = 100
    req.args = {'filter': query_filter}
    return superdesk.get_resource_service('auth').get(req, None)


def get_query_for_expired_sessions(expiration_time):
    query = {'and':
             [
                 {'range': {'auth._updated': {'lte': date_to_str(expiration_time)}}},
             ]
             }
    return superdesk.json.dumps(query)
