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
from datetime import timedelta

from flask import current_app as app
from werkzeug.exceptions import HTTPException
from settings import DAYS_TO_KEEP

import superdesk
from superdesk.notification import push_notification
from superdesk.io import providers
from superdesk.celery_app import celery
from superdesk.utc import utcnow
from superdesk.workflow import set_default_state


UPDATE_SCHEDULE_DEFAULT = {'minutes': 5}
LAST_UPDATED = 'last_updated'
STATE_INGESTED = 'ingested'


logger = logging.getLogger(__name__)


superdesk.workflow_state(STATE_INGESTED)

superdesk.workflow_action(
    name='ingest'
)


def is_valid_type(provider, provider_type_filter=None):
    """Test if given provider has valid type and should be updated.

    :param provider: provider to be updated
    :param provider_type_filter: active provider type filter
    """
    provider_type = provider.get('type')
    if provider_type not in providers:
        return False
    if provider_type_filter and provider_type != provider_type_filter:
        return False
    return True


def is_scheduled(provider):
    """Test if given provider should be scheduled for update.

    :param provider: ingest provider
    """
    now = utcnow()
    last_updated = provider.get(LAST_UPDATED, now - timedelta(days=100))  # if never updated run now
    update_schedule = provider.get('update_schedule', UPDATE_SCHEDULE_DEFAULT)
    return last_updated + timedelta(**update_schedule) < now


def is_closed(provider):
    """Test if provider is closed.

    :param provider: ingest provider
    """
    return provider.get('is_closed', False)


def filter_expired_items(provider, items):
    days_to_keep_content = provider.get('days_to_keep', DAYS_TO_KEEP)
    expiration_date = utcnow() - timedelta(days=days_to_keep_content)
    return [item for item in items if item.get('versioncreated', utcnow()) > expiration_date]


class UpdateIngest(superdesk.Command):
    """Update ingest providers."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in superdesk.get_resource_service('ingest_providers').get(req=None, lookup={}):
            if is_valid_type(provider, provider_type) and is_scheduled(provider) and not is_closed(provider):
                rule_set = None
                if provider.get('rule_set'):
                    rule_set = superdesk.get_resource_service('rule_sets').find_one(_id=provider['rule_set'], req=None)

                update_provider.delay(provider, rule_set)


@celery.task
def update_provider(provider, rule_set=None):
    """
    Fetches items from ingest provider as per the configuration, ingests them into Superdesk and
    updates the provider.
    """

    for items in providers[provider.get('type')].update(provider):
        ingest_items(items, provider, rule_set)

    superdesk.get_resource_service('ingest_providers').update(provider['_id'], {
        LAST_UPDATED: utcnow(),
        'config': provider.get('config', {}),  # persist changes to config if any
        app.config['ETAG']: provider.get(app.config['ETAG'])
    })

    logger.info('Provider {0} updated'.format(provider['_id']))
    push_notification('ingest:update')


def process_anpa_category(item):
    anpa_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')
    if anpa_categories:
        for anpa_category in anpa_categories['items']:
            if anpa_category['is_active'] is True \
                    and item['anpa-category']['qcode'].lower() == anpa_category['value'].lower():
                item['anpa-category'] = {'qcode': item['anpa-category']['qcode'], 'name': anpa_category['name']}
                break


def apply_rule_set(item, provider, rule_set=None):
    """
    Applies rules set on the item to be ingested into the system. If there's no rule set then the item will
    be returned without any change.

    :param item: Item to be ingested
    :param provider: provider object from whom the item was received
    :return: item
    """

    if rule_set is None and provider.get('rule_set') is not None:
        rule_set = superdesk.get_resource_service('rule_sets').find_one(_id=provider['rule_set'], req=None)

    if rule_set and 'body_html' in item:
        body = item['body_html']

        for rule in rule_set['rules']:
            body = body.replace(rule['old'], rule['new'])

        item['body_html'] = body

    return item


def ingest_items(items, provider, rule_set=None):
    for item in filter_expired_items(provider, items):
        item.setdefault('_id', item['guid'])

        item['ingest_provider'] = str(provider['_id'])
        item.setdefault('source', provider.get('source', ''))
        set_default_state(item, STATE_INGESTED)

        if 'anpa-category' in item:
            process_anpa_category(item)

        apply_rule_set(item, provider, rule_set)

        ingest_service = superdesk.get_resource_service('ingest')

        if item.get('ingest_provider_sequence') is None:
            ingest_service.set_ingest_provider_sequence(item, provider)

        old_item = ingest_service.find_one(_id=item['guid'], req=None)
        if old_item:
            ingest_service.put(item['guid'], item)
        else:
            try:
                ingest_service.post([item])
            except HTTPException as e:
                logger.error("Exception while persisting item in ingest collection", e)
                ingest_service.put(item['guid'], item)


superdesk.command('ingest:update', UpdateIngest())
