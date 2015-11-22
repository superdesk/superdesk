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
from flask import current_app as app, request
from superdesk import Resource, Service, config
from superdesk.resource import build_custom_hateoas
from superdesk.metadata.utils import item_url
from superdesk.utc import utcnow
from superdesk.errors import SuperdeskApiError
from superdesk.metadata.item import metadata_schema, ITEM_STATE, CONTENT_STATE
from superdesk.celery_app import celery
from apps.rules.routing_rules import Weekdays, set_time
from apps.archive.common import ARCHIVE, CUSTOM_HATEOAS
from flask import render_template_string


CONTENT_TEMPLATE_PRIVILEGE = 'content_templates'
TEMPLATE_FIELDS = {'template_name', 'template_type', 'schedule',
                   'last_run', 'next_run', 'template_desk', 'template_stage',
                   config.ID_FIELD, config.LAST_UPDATED, config.DATE_CREATED,
                   config.ETAG, 'task'}


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


class ContentTemplatesApplyResource(Resource):
    endpoint_name = 'content_templates_apply'
    resource_title = endpoint_name
    schema = {}
    schema.update(metadata_schema)
    resource_methods = ['POST']
    item_methods = []
    privileges = {'POST': ARCHIVE}
    url = 'content_templates/<{0}:template_name>/apply'.format(item_url)


class ContentTemplatesApplyService(Service):

    def create(self, docs, **kwargs):
        template_name = request.view_args['template_name']
        if not template_name:
            SuperdeskApiError.badRequestError(message='Invalid Template Name')

        pattern = '^{}$'.format(re.escape(template_name.strip()))
        query = {'template_name': re.compile(pattern, re.IGNORECASE)}
        template = superdesk.get_resource_service('content_templates').find_one(req=None, **query)
        if not template:
            SuperdeskApiError.badRequestError(message='Invalid Template')

        render_content_template(docs[0], template)
        build_custom_hateoas(CUSTOM_HATEOAS, docs[0])
        return [docs[0].get(config.ID_FIELD)]


def render_content_template(item, template):
    """
    Render the template.
    :param dict item: item on which template is applied
    :param dict template: template
    """
    for key, value in template.items():
        if key in TEMPLATE_FIELDS or template.get(key) is None:
            continue

        if isinstance(template.get(key), str):
            item[key] = render_template_string(template.get(key), item=item)
        elif (isinstance(template.get(key), dict) or isinstance(template.get(key), list)) and template.get(key):
            item[key] = template.get(key)
        elif not (isinstance(template.get(key), dict) or isinstance(template.get(key), list)):
            item[key] = template.get(key)

    if template.get('template_desk'):
        if not item.get('task'):
            item['task'] = {}

        item['task']['desk'] = template.get('template_desk')
        if template.get('template_stage'):
            item['task']['stage'] = template.get('template_stage')


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
