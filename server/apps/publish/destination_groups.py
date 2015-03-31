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
from eve.utils import ParsedRequest
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError

logger = logging.getLogger(__name__)


class DestinationGroupsResource(Resource):

    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True,
        },
        'description': {
            'type': 'string'
        },
        'destination_groups': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'group': Resource.rel('destination_groups', True)
                }
            }
        },
        'output_channels': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'channel': Resource.rel('output_channels', True),
                    'selector_codes': {
                        'type': 'list'
                    }
                }
            }
        }
    }

    datasource = {'default_sort': [('name', -1)]}
    privileges = {'POST': 'destination_groups', 'DELETE': 'destination_groups', 'PATCH': 'destination_groups'}


class DestinationGroupsService(BaseService):
    def on_create(self, docs):
        pass

    def on_update(self, updates, original):
        dest_groups = updates.get('destination_groups', [])
        if dest_groups:
            if self.__is_group_self_referenced(dest_groups):
                raise SuperdeskApiError.badRequestError(
                    message='Destination Group is resolves back to itself.')

    def on_delete(self, doc):
        parsed_request = ParsedRequest()
        parsed_request.args = {'destination_groups': doc.get('_id')}
        if list(get_resource_service('archive').find(req=parsed_request, lookup=None)).count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Destination Group is referenced by items.',
                payload={'item': 1})

        parsed_request = ParsedRequest()
        parsed_request.args = {'destination_groups.group': doc.get('_id')}
        if list(get_resource_service('destination_groups').find(req=parsed_request, lookup=None)).count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Destination Group is referenced by another destination group.',
                payload={'destination_group': 1})

    def __is_group_self_referenced(self):
        pass
