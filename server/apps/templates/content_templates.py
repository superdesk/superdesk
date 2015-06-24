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
from superdesk import Resource, Service
from superdesk.errors import SuperdeskApiError
from apps.content import metadata_schema

CONTENT_TEMPLATE_PRIVILEGE = 'content_templates'


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

    def on_update(self, updates, original):
        if 'template_name' in updates:
            updates['template_name'] = updates['template_name'].lower().strip()
            self.validate_template_name(updates['template_name'])

    def validate_template_name(self, doc_template_name):
        query = {'template_name': re.compile('^{}$'.format(doc_template_name), re.IGNORECASE)}
        if self.find_one(req=None, **query):
            msg = 'Template name must be unique'
            raise SuperdeskApiError.preconditionFailedError(message=msg, payload=msg)
