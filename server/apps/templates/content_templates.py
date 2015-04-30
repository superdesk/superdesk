# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import Resource
from apps.content import metadata_schema

CONTENT_TEMPLATE_PRIVILEGE = 'content_templates'

class ContentTemplatesResource(Resource):
    schema = {
        'template_name': {
            'type': 'string',
            'iunique': True
        },
        'destination_groups': {
            'type': 'list',
            'schema': Resource.rel('destination_groups', True)
        }
    }

    schema.update(metadata_schema)
    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH', 'DELETE']
    privileges = {'POST': CONTENT_TEMPLATE_PRIVILEGE,
                  'PATCH': CONTENT_TEMPLATE_PRIVILEGE,
                  'DELETE': CONTENT_TEMPLATE_PRIVILEGE}
