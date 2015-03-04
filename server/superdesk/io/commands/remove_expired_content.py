# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
import superdesk
from eve.utils import ParsedRequest, date_to_str
from datetime import timedelta
from superdesk.utc import utcnow
from superdesk.notification import push_notification
from superdesk.io.ingest_provider_model import INGEST_EXPIRY_MINUTES
from superdesk.errors import ProviderError
from superdesk.stats import stats


logger = logging.getLogger(__name__)


class RemoveExpiredContent(superdesk.Command):
    """Remove stale data from ingest based on the provider settings."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in superdesk.get_resource_service('ingest_providers').get(req=None, lookup={}):
            if not provider_type or provider_type == provider.get('type'):
                try:
                    remove_expired_data(provider)
                except (Exception) as err:
                    logger.exception(err)
                    raise ProviderError.expiredContentError(err, provider)
                finally:
                    push_notification('ingest:cleaned')


superdesk.command('ingest:clean_expired', RemoveExpiredContent())


def remove_expired_data(provider):
    """Remove expired data for provider"""
    print('Removing expired content for provider: %s' % provider['_id'])
    minutes_to_keep_content = provider.get('content_expiry', INGEST_EXPIRY_MINUTES)
    expiration_date = utcnow() - timedelta(minutes=minutes_to_keep_content)

    items = get_expired_items(str(provider['_id']), expiration_date)
    if items.count() > 0:
        for item in items:
            print('Removing item %s' % item['_id'])
            superdesk.get_resource_service('ingest').delete_action({'_id': str(item['_id'])})
            if not item.get('archived'):
                for file_id in [rend.get('media') for rend in item.get('renditions', {}).values()
                                if rend.get('media')]:
                    superdesk.app.media.delete(file_id)

    stats.incr('ingest.expired_items', items.count())
    print('Removed expired content for provider: %s' % provider['_id'])


def get_expired_items(provider_id, expiration_date):
    query_filter = get_query_for_expired_items(provider_id, expiration_date)
    req = ParsedRequest()
    req.max_results = 100
    req.args = {'filter': query_filter}
    return superdesk.get_resource_service('ingest').get(req, None)


def get_query_for_expired_items(provider_id, expiration_date):
    """Find all ingest items with given provider id and
    (expiry is past or
    (no expiry assigned and versioncreated is less then calculated expiry date))"""
    query = {'and': [
        {'term': {'ingest.ingest_provider': provider_id}},
        {'or': [
            {'range': {'ingest.expiry': {'lte': date_to_str(utcnow())}}},
            {'and': [{'missing': {'field': 'ingest.expiry'}},
                     {'range': {'ingest.versioncreated': {'lte': date_to_str(expiration_date)}}}]},
        ]},
    ]}

    return superdesk.json.dumps(query)
