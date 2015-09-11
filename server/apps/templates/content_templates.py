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
from superdesk import Resource, Service
from superdesk.utc import utcnow
from superdesk.errors import SuperdeskApiError
from superdesk.metadata.item import metadata_schema
from apps.rules.routing_rules import WEEKDAYS, parse_time

CONTENT_TEMPLATE_PRIVILEGE = 'content_templates'


def get_next_run(schedule, now=None):
    """Get next run time based on schedule.

    Schedule is day of week and time.

    :param dict schedule: dict with `day_of_week` and `create_at` params
    :param datetime now
    :return datetime
    """
    allowed_days = [WEEKDAYS.index(day.upper()) for day in schedule.get('day_of_week')]
    if not allowed_days:
        return None

    if now is None:
        now = utcnow()
    next_run = parse_time(now, schedule.get('create_at'))

    if next_run < now:
        # if the time passed already skip today
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
            'allowed': ['create', 'kill'],
            'default': 'create',
        },
        'template_desk': Resource.rel('desks', embeddable=False, nullable=True),
        'schedule': {'type': 'dict'},
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
            updates['last_run'] = original.get('next_run')
            updates['next_run'] = get_next_run(updates.get('schedule'))

    def validate_template_name(self, doc_template_name):
        query = {'template_name': re.compile('^{}$'.format(doc_template_name), re.IGNORECASE)}
        if self.find_one(req=None, **query):
            msg = 'Template name must be unique'
            raise SuperdeskApiError.preconditionFailedError(message=msg, payload=msg)
