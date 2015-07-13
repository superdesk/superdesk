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
from settings import INGEST_EXPIRY_MINUTES
from datetime import timedelta, timezone, datetime
from werkzeug.exceptions import HTTPException

from superdesk.notification import push_notification
from superdesk.activity import ACTIVITY_EVENT, notify_and_add_activity
from superdesk.io import providers
from superdesk.celery_app import celery
from superdesk.utc import utcnow, get_expiry_date
from superdesk.workflow import set_default_state
from superdesk.errors import ProviderError
from superdesk.stats import stats
from superdesk.upload import url_for_media
from superdesk.media.media_operations import download_file_from_url, process_file
from superdesk.media.renditions import generate_renditions
from superdesk.io.iptc import subject_codes
from apps.archive.common import generate_guid, GUID_NEWSML, GUID_FIELD, FAMILY_ID
from superdesk.celery_task_utils import mark_task_as_not_running, is_task_running


UPDATE_SCHEDULE_DEFAULT = {'minutes': 5}
LAST_UPDATED = 'last_updated'
LAST_ITEM_UPDATE = 'last_item_update'
STATE_INGESTED = 'ingested'
IDLE_TIME_DEFAULT = {'hours': 0, 'minutes': 0}


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
    def is_not_expired(item):
        if item.get('expiry') or item.get('versioncreated'):
            expiry = item.get('expiry', item['versioncreated'] + delta)
            if expiry.tzinfo:
                return expiry > utcnow()
        return False

    try:
        delta = timedelta(minutes=provider.get('content_expiry', INGEST_EXPIRY_MINUTES))
        return [item for item in items if is_not_expired(item)]
    except Exception as ex:
        raise ProviderError.providerFilterExpiredContentError(ex, provider)


def get_provider_rule_set(provider):
    if provider.get('rule_set'):
        return superdesk.get_resource_service('rule_sets').find_one(_id=provider['rule_set'], req=None)


def get_provider_routing_scheme(provider):
    if provider.get('routing_scheme'):
        return superdesk.get_resource_service('routing_schemes').find_one(_id=provider['routing_scheme'], req=None)


def get_task_ttl(provider):
    update_schedule = provider.get('update_schedule', UPDATE_SCHEDULE_DEFAULT)
    return update_schedule.get('minutes', 0) * 60 + update_schedule.get('hours', 0) * 3600


def get_is_idle(providor):
    last_item = providor.get(LAST_ITEM_UPDATE)
    idle_time = providor.get('idle_time', IDLE_TIME_DEFAULT)
    if isinstance(idle_time['hours'], datetime):
        idle_hours = 0
    else:
        idle_hours = idle_time['hours']
    if isinstance(idle_time['minutes'], datetime):
        idle_minutes = 0
    else:
        idle_minutes = idle_time['minutes']
    # there is an update time and the idle time is none zero
    if last_item and (idle_hours != 0 or idle_minutes != 0):
        if utcnow() > last_item + timedelta(hours=idle_hours, minutes=idle_minutes):
            return True
    return False


def get_task_id(provider):
    return 'update-ingest-{0}-{1}'.format(provider.get('name'), provider.get(superdesk.config.ID_FIELD))


def is_updatable(provider):
    """Test if given provider has service that can update it.

    :param provider
    """
    service = providers.get(provider.get('type'))
    return hasattr(service, 'update')


class UpdateIngest(superdesk.Command):
    """Update ingest providers."""

    option_list = (
        superdesk.Option('--provider', '-p', dest='provider_type'),
    )

    def run(self, provider_type=None):
        for provider in superdesk.get_resource_service('ingest_providers').get(req=None, lookup={}):
            if (is_valid_type(provider, provider_type) and is_updatable(provider)
               and is_scheduled(provider) and not is_closed(provider)):
                kwargs = {
                    'provider': provider,
                    'rule_set': get_provider_rule_set(provider),
                    'routing_scheme': get_provider_routing_scheme(provider)
                }
                update_provider.apply_async(
                    expires=get_task_ttl(provider),
                    kwargs=kwargs)


@celery.task(soft_time_limit=1800)
def update_provider(provider, rule_set=None, routing_scheme=None):
    """
    Fetches items from ingest provider as per the configuration, ingests them into Superdesk and
    updates the provider.
    """
    if is_task_running(provider['name'],
                       provider[superdesk.config.ID_FIELD],
                       provider.get('update_schedule', UPDATE_SCHEDULE_DEFAULT)):
        return

    if provider.get('type') == 'search':
        return

    if not is_updatable(provider):
        return

    try:
        update = {
            LAST_UPDATED: utcnow()
        }

        for items in providers[provider.get('type')].update(provider):
            ingest_items(items, provider, rule_set, routing_scheme)
            stats.incr('ingest.ingested_items', len(items))
            if items:
                update[LAST_ITEM_UPDATE] = utcnow()
        ingest_service = superdesk.get_resource_service('ingest_providers')
        ingest_service.system_update(provider[superdesk.config.ID_FIELD], update, provider)

        if LAST_ITEM_UPDATE not in update and get_is_idle(provider):
            notify_and_add_activity(
                ACTIVITY_EVENT,
                'Provider {{name}} has gone strangely quiet. Last activity was on {{last}}',
                resource='ingest_providers',
                user_list=ingest_service._get_administrators(),
                name=provider.get('name'),
                last=provider[LAST_ITEM_UPDATE].replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%c"))

        logger.info('Provider {0} updated'.format(provider[superdesk.config.ID_FIELD]))
        push_notification('ingest:update', provider_id=str(provider[superdesk.config.ID_FIELD]))
    finally:
        mark_task_as_not_running(provider['name'],
                                 provider[superdesk.config.ID_FIELD])


def process_anpa_category(item, provider):
    try:
        anpa_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')
        if anpa_categories:
            for item_category in item['anpa_category']:
                for anpa_category in anpa_categories['items']:
                    if anpa_category['is_active'] is True \
                            and item_category['qcode'].lower() == anpa_category['qcode'].lower():
                        item_category['name'] = anpa_category['name']
                        break
    except Exception as ex:
        raise ProviderError.anpaError(ex, provider)


def process_iptc_codes(item, provider):
    """
    Ensures that the higher level IPTC codes are present by inserting them if missing, for example
    if given 15039001 (Formula One) make sure that 15039000 (motor racing) and 15000000 (sport) are there as well

    :param item: A story item
    :return: A story item with possible expanded subjects
    """
    try:
        def iptc_already_exists(code):
            for entry in item['subject']:
                if 'qcode' in entry and code == entry['qcode']:
                    return True
            return False

        for subject in item['subject']:
            if 'qcode' in subject and len(subject['qcode']) == 8:
                top_qcode = subject['qcode'][:2] + '000000'
                if not iptc_already_exists(top_qcode):
                    item['subject'].append({'qcode': top_qcode, 'name': subject_codes[top_qcode]})

                mid_qcode = subject['qcode'][:5] + '000'
                if not iptc_already_exists(mid_qcode):
                    item['subject'].append({'qcode': mid_qcode, 'name': subject_codes[mid_qcode]})
    except Exception as ex:
        raise ProviderError.iptcError(ex, provider)


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


def ingest_items(items, provider, rule_set=None, routing_scheme=None):
    all_items = filter_expired_items(provider, items)
    items_dict = {doc[GUID_FIELD]: doc for doc in all_items}
    items_in_package = []
    failed_items = set()

    for item in [doc for doc in all_items if doc.get('type') == 'composite']:
        items_in_package = [ref['residRef'] for group in item.get('groups', [])
                            for ref in group.get('refs', []) if 'residRef' in ref]

    for item in [doc for doc in all_items if doc.get('type') != 'composite']:
        ingested = ingest_item(item, provider, rule_set,
                               routing_scheme=routing_scheme if not item[GUID_FIELD] in items_in_package else None)
        if not ingested:
            failed_items.add(item[GUID_FIELD])

    for item in [doc for doc in all_items if doc.get('type') == 'composite']:
        for ref in [ref for group in item.get('groups', [])
                    for ref in group.get('refs', []) if 'residRef' in ref]:
            if ref['residRef'] in failed_items:
                failed_items.add(item[GUID_FIELD])
                continue

            ref.setdefault('location', 'ingest')
            itemRendition = items_dict.get(ref['residRef'], {}).get('renditions')
            if itemRendition:
                ref.setdefault('renditions', itemRendition)
            ref[GUID_FIELD] = ref['residRef']
            if items_dict.get(ref['residRef']):
                ref['residRef'] = items_dict.get(ref['residRef'], {}).get(superdesk.config.ID_FIELD)
        if item[GUID_FIELD] in failed_items:
            continue

        ingested = ingest_item(item, provider, rule_set, routing_scheme)
        if not ingested:
            failed_items.add(item[GUID_FIELD])

    app.data._search_backend('ingest').bulk_insert('ingest', [item for item in all_items
                                                              if item[GUID_FIELD] not in failed_items])
    if failed_items:
        logger.error('Failed to ingest the following items: %s', failed_items)
    return failed_items


def ingest_item(item, provider, rule_set=None, routing_scheme=None):
    try:
        item.setdefault(superdesk.config.ID_FIELD, generate_guid(type=GUID_NEWSML))
        item[FAMILY_ID] = item[superdesk.config.ID_FIELD]
        providers[provider.get('type')].provider = provider

        item['ingest_provider'] = str(provider[superdesk.config.ID_FIELD])
        item.setdefault('source', provider.get('source', ''))
        set_default_state(item, STATE_INGESTED)
        item['expiry'] = get_expiry_date(provider.get('content_expiry', INGEST_EXPIRY_MINUTES),
                                         item.get('versioncreated'))

        if 'anpa_category' in item:
            process_anpa_category(item, provider)

        if 'subject' in item:
            process_iptc_codes(item, provider)

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

        old_item = ingest_service.find_one(guid=item[GUID_FIELD], req=None)

        if old_item:
            # In case we already have the item, preserve the _id
            item[superdesk.config.ID_FIELD] = old_item[superdesk.config.ID_FIELD]
            ingest_service.put_in_mongo(item[superdesk.config.ID_FIELD], item)
        else:
            try:
                ingest_service.post_in_mongo([item])
            except HTTPException as e:
                logger.error("Exception while persisting item in ingest collection", e)

        if routing_scheme:
            routed = ingest_service.find_one(_id=item[superdesk.config.ID_FIELD], req=None)
            superdesk.get_resource_service('routing_schemes').apply_routing_scheme(routed, provider, routing_scheme)
    except Exception as ex:
        logger.exception(ex)
        try:
            superdesk.app.sentry.captureException()
        except:
            pass
        return False
    return True


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
    except Exception:
        for file_id in inserted:
            app.media.delete(file_id)
        raise


superdesk.command('ingest:update', UpdateIngest())
