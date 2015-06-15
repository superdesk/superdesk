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
from superdesk.resource import Resource
from superdesk.services import BaseService

logger = logging.getLogger(__name__)


class PublishFilterResource(Resource):
    schema = {
        'blocking_filter': {
            'type': 'list',
            'schema': {
                'type': 'list',
                'schema': {
                    'filter_expression': Resource.rel('filter_condition')
                }
            }
        },
        'name': {
            'type': 'string',
            'nullable': False,
        },
        'mongo_query': {
            'type': 'string',
            'nullable': True
        },
        'elastic_query': {
            'type': 'string',
            'nullable': True
        }
    }

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'name'
    }

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}


class BlockingFilterService(BaseService):
    pass
