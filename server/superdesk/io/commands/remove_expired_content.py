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
        providers = [p for p in superdesk.get_resource_service('ingest_providers').get(req=None, lookup={})]
        self.remove_expired({'exclude': [str(p.get('_id')) for p in providers]})
        for provider in providers:
            if not provider_type or provider_type == provider.get('type'):
                self.remove_expired(provider)

    def remove_expired(self, provider):
        try:
            remove_expired_data(provider)
            push_notification('ingest:cleaned')
        except (Exception) as err:
            logger.exception(err)
            raise ProviderError.expiredContentError(err, provider)


superdesk.command('ingest:clean_expired', RemoveExpiredContent())


def remove_expired_data(provider):
    """Remove expired data for provider"""
    print('Removing expired content for provider: %s' % provider.get('_id', 'Detached items'))
    minutes_to_keep_content = provider.get('content_expiry', INGEST_EXPIRY_MINUTES)
    expiration_date = utcnow() - timedelta(minutes=minutes_to_keep_content)
    ingest_service = superdesk.get_resource_service('ingest')

    items = get_expired_items(provider, expiration_date)

    ids = [item['_id'] for item in items]
    file_ids = [rend.get('media')
                for item in items
                for rend in item.get('renditions', {}).values()
                if not item.get('archived') and rend.get('media')]

    if ids:
        print('Removing items %s' % ids)
        ingest_service.delete({'_id': {'$in': ids}})

    for file_id in file_ids:
        print('Deleting file: ', file_id)
        superdesk.app.media.delete(file_id)

    stats.incr('ingest.expired_items', len(ids))
    print('Removed expired content for provider: {0} count: {1}'
          .format(provider.get('_id', 'Detached items'), len(ids)))


def get_expired_items(provider_id, expiration_date):
    query_filter = get_query_for_expired_items(provider_id, expiration_date)
    return superdesk.get_resource_service('ingest').get_from_mongo(lookup=query_filter, req=None)


def get_query_for_expired_items(provider, expiration_date):
    """Find all ingest items with given provider id and
    (expiry is past or
    (no expiry assigned and versioncreated is less then calculated expiry date))"""
    query = {
        '$or': [
            {'expiry': {'$lte': utcnow()}},
            {
                'versioncreated': {'$lte': expiration_date},
                'expiry': {'$exists': False}
            }
        ]
    }

    if provider.get('_id'):
        query['ingest_provider'] = str(provider.get('_id'))

    if provider.get('exclude'):
        excluded = provider.get('exclude')
        query['ingest_provider'] = {'$nin': excluded}

    return query
