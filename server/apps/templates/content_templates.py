# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import re
import datetime
import superdesk
from flask import current_app as app
from superdesk import Resource, Service, config
from superdesk.utils import SuperdeskBaseEnum
from superdesk.resource import build_custom_hateoas
from superdesk.utc import utcnow
from superdesk.errors import SuperdeskApiError
from superdesk.metadata.item import metadata_schema, ITEM_STATE, CONTENT_STATE
from superdesk.celery_app import celery
from apps.rules.routing_rules import Weekdays, set_time
from apps.archive.common import ARCHIVE, CUSTOM_HATEOAS, item_schema, format_dateline_to_locmmmddsrc
from apps.auth import get_user
from flask import render_template_string


CONTENT_TEMPLATE_PRIVILEGE = 'content_templates'
TEMPLATE_FIELDS = {'template_name', 'template_type', 'schedule',
                   'last_run', 'next_run', 'template_desk', 'template_stage',
                   config.ID_FIELD, config.LAST_UPDATED, config.DATE_CREATED,
                   config.ETAG, 'task'}
KILL_TEMPLATE_NOT_REQUIRED_FIELDS = ['schedule', 'dateline', 'template_desk', 'template_stage']


class TemplateType(SuperdeskBaseEnum):
    KILL = 'kill'
    CREATE = 'create'
    HIGHLIGHTS = 'highlights'


def get_next_run(schedule, now=None):
    """Get next run time based on schedule.

    Schedule is day of week and time.

    :param dict schedule: dict with `day_of_week` and `create_at` params
    :param datetime now
    :return datetime
    """
    if not schedule.get('is_active', False):
        return None

    allowed_days = [Weekdays[day.upper()].value for day in schedule.get('day_of_week', [])]
    if not allowed_days:
        return None

    if now is None:
        now = utcnow()

    now = now.replace(second=0)
    next_run = set_time(now, schedule.get('create_at'))

    # if the time passed already today do it tomorrow earliest
    if next_run <= now:
        next_run += datetime.timedelta(days=1)

    while next_run.weekday() not in allowed_days:
        next_run += datetime.timedelta(days=1)

    return next_run


class ContentTemplatesResource(Resource):
    schema = {
        'data': {
            'type': 'dict',
            'schema': metadata_schema,
        },

        'template_name': {
            'type': 'string',
            'iunique': True,
            'required': True,
        },

        'template_type': {
            'type': 'string',
            'required': True,
            'allowed': TemplateType.values(),
            'default': TemplateType.CREATE.value,
        },

        'template_desk': Resource.rel('desks', embeddable=False, nullable=True),

        'template_stage': Resource.rel('stages', embeddable=False, nullable=True),

        'schedule': {'type': 'dict', 'schema': {
            'is_active': {'type': 'boolean'},
            'create_at': {'type': 'string'},
            'day_of_week': {'type': 'list'},
        }},

        'last_run': {'type': 'datetime', 'readonly': True},
        'next_run': {'type': 'datetime', 'readonly': True},

        'user': Resource.rel('users'),
        'is_private': {'type': 'boolean', 'default': True},
    }

    additional_lookup = {
        'url': 'regex("[\w]+")',
        'field': 'template_name'
    }

    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH', 'DELETE']
    privileges = {'POST': CONTENT_TEMPLATE_PRIVILEGE,
                  'PATCH': CONTENT_TEMPLATE_PRIVILEGE,
                  'DELETE': CONTENT_TEMPLATE_PRIVILEGE}


class ContentTemplatesService(Service):

    def on_create(self, docs):
        for doc in docs:
            doc['template_name'] = doc['template_name'].lower().strip()
            if doc.get('schedule'):
                doc['next_run'] = get_next_run(doc.get('schedule'))

            if doc.get('template_type') == TemplateType.KILL.value and \
                    any(key for key in doc.keys() if key in KILL_TEMPLATE_NOT_REQUIRED_FIELDS):
                raise SuperdeskApiError.badRequestError(
                    message="Invalid kill template. "
                            "{} are not allowed".format(', '.join(KILL_TEMPLATE_NOT_REQUIRED_FIELDS)))
            if get_user():
                doc.setdefault('user', get_user()[config.ID_FIELD])

    def on_update(self, updates, original):
        if updates.get('template_type') and updates.get('template_type') != original.get('template_type') and \
           updates.get('template_type') == TemplateType.KILL.value:
            self._process_kill_template(updates)

        if updates.get('schedule'):
            updates['next_run'] = get_next_run(updates.get('schedule'))

    def get_scheduled_templates(self, now):
        """
        Get the template by schedule
        :param datetime now:
        :return MongoCursor:
        """
        query = {'next_run': {'$lte': now}, 'schedule.is_active': True}
        return self.find(query)

    def get_template_by_name(self, template_name):
        """
        Get the template by name
        :param str template_name: template name
        :return dict: template
        """
        query = {'template_name': re.compile('^{}$'.format(template_name), re.IGNORECASE)}
        return self.find_one(req=None, **query)

    def _process_kill_template(self, doc):
        """
        Marks certain field required by the kill as null.
        """
        if doc.get('template_type') != TemplateType.KILL.value:
            return

        for key in KILL_TEMPLATE_NOT_REQUIRED_FIELDS:
            if key in metadata_schema:
                doc.setdefault('data', {})
                doc['data'][key] = None
            else:
                doc[key] = None


class ContentTemplatesApplyResource(Resource):
    endpoint_name = 'content_templates_apply'
    resource_title = endpoint_name
    schema = {
        'template_name': {
            'type': 'string',
            'required': True
        },
        'item': {
            'type': 'dict',
            'required': True,
            'schema': item_schema()
        }
    }

    resource_methods = ['POST']
    item_methods = []
    privileges = {'POST': ARCHIVE}
    url = 'content_templates_apply'


class ContentTemplatesApplyService(Service):

    def create(self, docs, **kwargs):
        doc = docs[0] if len(docs) > 0 else {}
        template_name = doc.get('template_name')
        item = doc.get('item') or {}

        if not template_name:
            SuperdeskApiError.badRequestError(message='Invalid Template Name')

        if not item:
            SuperdeskApiError.badRequestError(message='Invalid Item')

        template = superdesk.get_resource_service('content_templates').get_template_by_name(template_name)
        if not template:
            SuperdeskApiError.badRequestError(message='Invalid Template')

        updates = render_content_template(item, template)
        item.update(updates)
        docs[0] = item
        build_custom_hateoas(CUSTOM_HATEOAS, docs[0])
        return [docs[0].get(config.ID_FIELD)]


def render_content_template(item, template):
    """
    Render the template.
    :param dict item: item on which template is applied
    :param dict template: template
    :return dict: updates to the item
    """
    updates = {}
    template_data = template.get('data', {})
    for key, value in template_data.items():
        if key in TEMPLATE_FIELDS or template_data.get(key) is None:
            continue

        if isinstance(value, str):
            updates[key] = render_template_string(value, item=item)
        elif (isinstance(value, dict) or isinstance(value, list)) and value:
            updates[key] = value
        elif not (isinstance(value, dict) or isinstance(value, list)):
            updates[key] = value

    if template.get('template_desk'):
        updates['task'] = {}
        updates['task']['desk'] = template.get('template_desk')
        if template.get('template_stage'):
            updates['task']['stage'] = template.get('template_stage')

    return updates


def get_scheduled_templates(now):
    """Get templates that should be used to create items for given time.

    :param datetime now
    :return Cursor
    """
    return superdesk.get_resource_service('content_templates').get_scheduled_templates(now)


def set_template_timestamps(template, now):
    """Update template `next_run` field to next time it should run.

    :param dict template
    :param datetime now
    """
    updates = {
        'last_run': now,
        'next_run': get_next_run(template.get('schedule'), now),
    }
    service = superdesk.get_resource_service('content_templates')
    service.update(template['_id'], updates, template)


def get_item_from_template(template):
    """Get item dict using data from template.

    :param dict template
    """
    item = template.get('data', {})
    item[ITEM_STATE] = CONTENT_STATE.SUBMITTED
    item['task'] = {'desk': template.get('template_desk'), 'stage': template.get('template_stage')}
    item['template'] = template.get('_id')
    item.pop('firstcreated', None)
    item.pop('versioncreated', None)

    # handle dateline
    dateline = item.get('dateline', {})
    dateline['date'] = utcnow()
    if dateline.get('located'):
        dateline['text'] = format_dateline_to_locmmmddsrc(dateline['located'], dateline['date'])

    return item


@celery.task(soft_time_limit=120)
def create_scheduled_content(now=None):
    if now is None:
        now = utcnow()
    templates = get_scheduled_templates(now)
    production = superdesk.get_resource_service(ARCHIVE)
    for template in templates:
        try:
            set_template_timestamps(template, now)
            item = get_item_from_template(template)
            production.post([item])
        except app.data.OriginalChangedError:
            pass  # ignore template if it changed meanwhile
