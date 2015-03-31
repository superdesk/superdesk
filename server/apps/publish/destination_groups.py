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
            if self.is_group_self_referenced(original[superdesk.config.ID_FIELD], dest_groups):
                raise SuperdeskApiError.badRequestError(
                    message='Circular dependency in Destination Group.')

    def on_delete(self, doc):
        archive_content = get_resource_service('archive')\
            .get(req=None, lookup={'destination_groups': doc.get(superdesk.config.ID_FIELD)})
        if archive_content and archive_content.count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Destination Group is referenced by items.',
                payload={'item': 1})

        dest_groups = self.get(req=None, lookup={'destination_groups.group': doc.get(superdesk.config.ID_FIELD)})
        if dest_groups and dest_groups.count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Destination Group is referenced by another destination group.',
                payload={'destination_group': 1})

    def is_group_self_referenced(self, dest_group_id, dest_groups):
        dest_groups = dest_groups or []
        for dest_group in dest_groups:
            if dest_group_id == dest_group['group']:
                return True

            group = self.find_one(req=None, _id=dest_group['group'])
            referenced_groups = group.get('destination_groups', [])
            if referenced_groups:
                return self.is_group_self_referenced(dest_group_id, referenced_groups)

        return False
