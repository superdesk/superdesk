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

from flask import current_app as app
from settings import DAYS_TO_KEEP
from datetime import timedelta
from werkzeug.exceptions import HTTPException

from superdesk.notification import push_notification
from superdesk.io import providers
from superdesk.celery_app import celery
from superdesk.utc import utcnow
from superdesk.workflow import set_default_state
from superdesk.errors import ProviderError
from superdesk.stats import stats
from superdesk.upload import url_for_media
from superdesk.media.media_operations import download_file_from_url, process_file
from superdesk.media.renditions import generate_renditions


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
    try:
        days_to_keep_content = provider.get('days_to_keep', DAYS_TO_KEEP)
        expiration_date = utcnow() - timedelta(days=days_to_keep_content)
        return [item for item in items if item.get('versioncreated', utcnow()) > expiration_date]
    except Exception as ex:
        raise ProviderError.providerFilterExpiredContentError(ex, provider)


def get_provider_rule_set(provider):
    if provider.get('rule_set'):
        return superdesk.get_resource_service('rule_sets').find_one(_id=provider['rule_set'], req=None)


def get_task_ttl(provider):
    update_schedule = provider.get('update_schedule', UPDATE_SCHEDULE_DEFAULT)
    return update_schedule.get('minutes', 0) * 60 + update_schedule.get('hours', 0) * 3600


def get_task_id(provider):
    return 'update-ingest-{0}-{1}'.format(provider.get('name'), provider.get('_id'))


class UpdateIngest(superdesk.Command):
    """Update ingest providers."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in superdesk.get_resource_service('ingest_providers').get(req=None, lookup={}):
            if is_valid_type(provider, provider_type) and is_scheduled(provider) and not is_closed(provider):
                kwargs = {
                    'provider': provider,
                    'rule_set': get_provider_rule_set(provider)
                }
                update_provider.apply_async(
                    task_id=get_task_id(provider),
                    expires=get_task_ttl(provider),
                    kwargs=kwargs)


@celery.task
def update_provider(provider, rule_set=None):
    """
    Fetches items from ingest provider as per the configuration, ingests them into Superdesk and
    updates the provider.
    """
    superdesk.get_resource_service('ingest_providers').update(provider['_id'], {
        LAST_UPDATED: utcnow(),
        # Providing the _etag as system updates to the documents shouldn't override _etag.
        app.config['ETAG']: provider.get(app.config['ETAG'])
    })

    for items in providers[provider.get('type')].update(provider):
        ingest_items(items, provider, rule_set)
        stats.incr('ingest.ingested_items', len(items))

    logger.info('Provider {0} updated'.format(provider['_id']))
    push_notification('ingest:update')


def process_anpa_category(item, provider):
    try:
        anpa_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')
        if anpa_categories:
            for anpa_category in anpa_categories['items']:
                if anpa_category['is_active'] is True \
                        and item['anpa-category']['qcode'].lower() == anpa_category['value'].lower():
                    item['anpa-category'] = {'qcode': item['anpa-category']['qcode'], 'name': anpa_category['name']}
                    break
    except Exception as ex:
        raise ProviderError.anpaError(ex, provider)


def apply_rule_set(item, provider, rule_set=None):
    """
    Applies rules set on the item to be ingested into the system. If there's no rule set then the item will
    be returned without any change.

    :param item: Item to be ingested
    :param provider: provider object from whom the item was received
    :return: item
    """
    try:
        if rule_set is None and provider.get('rule_set') is not None:
            rule_set = superdesk.get_resource_service('rule_sets').find_one(_id=provider['rule_set'], req=None)

            if rule_set and 'body_html' in item:
                body = item['body_html']

                for rule in rule_set['rules']:
                    body = body.replace(rule['old'], rule['new'])

                item['body_html'] = body

        return item
    except Exception as ex:
        raise ProviderError.ruleError(ex, provider)


def ingest_items(items, provider, rule_set=None):
    all_items = filter_expired_items(provider, items)
    items_dict = {doc['guid']: doc for doc in all_items}

    for item in [doc for doc in all_items if doc.get('type') != 'composite']:
        ingest_item(item, provider, rule_set)

    for item in [doc for doc in all_items if doc.get('type') == 'composite']:
        for ref in [ref for group in item.get('groups', [])
                    for ref in group.get('refs', []) if 'residRef' in ref]:
            ref.setdefault('location', 'ingest')
            itemRendition = items_dict.get(ref['residRef'], {}).get('renditions')
            if itemRendition:
                ref.setdefault('renditions', itemRendition)
        ingest_item(item, provider, rule_set)


def ingest_item(item, provider, rule_set=None):
    try:
        item.setdefault('_id', item['guid'])
        providers[provider.get('type')].provider = provider

        item['ingest_provider'] = str(provider['_id'])
        item.setdefault('source', provider.get('source', ''))
        set_default_state(item, STATE_INGESTED)

        if 'anpa-category' in item:
            process_anpa_category(item, provider)

        apply_rule_set(item, provider, rule_set)

        ingest_service = superdesk.get_resource_service('ingest')

        if item.get('ingest_provider_sequence') is None:
            ingest_service.set_ingest_provider_sequence(item, provider)

        rend = item.get('renditions', {})
        if rend:
            baseImageRend = rend.get('baseImage') or next(iter(rend.values()))
            if baseImageRend:
                href = providers[provider.get('type')].prepare_href(baseImageRend['href'])
                update_renditions(item, href)

        old_item = ingest_service.find_one(_id=item['guid'], req=None)

        if old_item:
            ingest_service.put(item['guid'], item)
        else:
            try:
                ingest_service.post([item])
            except HTTPException as e:
                logger.error("Exception while persisting item in ingest collection", e)
                ingest_service.put(item['guid'], item)
    except ProviderError:
        raise
    except Exception as ex:
        raise ProviderError.ingestError(ex, provider)


def update_renditions(item, href):
    inserted = []
    try:
        content, filename, content_type = download_file_from_url(href)
        file_type, ext = content_type.split('/')
        metadata = process_file(content, file_type)
        file_guid = app.media.put(content, filename, content_type, metadata)
        inserted.append(file_guid)

        rendition_spec = app.config.get('RENDITIONS', {}).get('picture', {})
        renditions = generate_renditions(content, file_guid, inserted, file_type,
                                         content_type, rendition_spec, url_for_media)
        item['renditions'] = renditions
        item['mimetype'] = content_type
        item['filemeta'] = metadata
    except Exception as io:
        logger.exception(io)
        for file_id in inserted:
            app.media.delete(file_id)
        raise


superdesk.command('ingest:update', UpdateIngest())
