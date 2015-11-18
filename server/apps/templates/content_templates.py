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
from superdesk import Resource, Service
from superdesk.utc import utcnow
from superdesk.errors import SuperdeskApiError
from superdesk.metadata.item import metadata_schema, ITEM_STATE, CONTENT_STATE
from superdesk.celery_app import celery
from apps.rules.routing_rules import Weekdays, set_time
from apps.archive.common import ARCHIVE


CONTENT_TEMPLATE_PRIVILEGE = 'content_templates'


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
        'template_name': {
            'type': 'string',
            'iunique': True,
            'required': True,
        },
        'template_type': {
            'type': 'string',
            'required': True,
            'allowed': ['create', 'kill', 'highlights'],
            'default': 'create',
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
    }

    schema.update(metadata_schema)
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
            self.validate_template_name(doc['template_name'])
            if doc.get('schedule'):
                doc['next_run'] = get_next_run(doc.get('schedule'))

    def on_update(self, updates, original):
        if 'template_name' in updates:
            updates['template_name'] = updates['template_name'].lower().strip()
            self.validate_template_name(updates['template_name'])
        if updates.get('schedule'):
            updates['next_run'] = get_next_run(updates.get('schedule'))

    def validate_template_name(self, doc_template_name):
        query = {'template_name': re.compile('^{}$'.format(doc_template_name), re.IGNORECASE)}
        if self.find_one(req=None, **query):
            msg = 'Template name must be unique'
            raise SuperdeskApiError.preconditionFailedError(message=msg, payload=msg)

    def get_scheduled_templates(self, now):
        query = {'next_run': {'$lte': now}, 'schedule.is_active': True}
        return self.find(query)


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
    item = {key: value for key, value in template.items() if key in metadata_schema}
    item[ITEM_STATE] = CONTENT_STATE.SUBMITTED
    item['task'] = {'desk': template.get('template_desk'), 'stage': template.get('template_stage')}
    item['template'] = item.pop('_id')
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
