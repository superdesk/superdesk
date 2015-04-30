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
import json
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from eve.utils import ParsedRequest

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
            'schema': Resource.rel('destination_groups', True)
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
    def on_update(self, updates, original):
        self.__validate_self_referenced(original[superdesk.config.ID_FIELD], updates.get('destination_groups', []))

    def on_delete(self, doc):
        doc_id = doc.get(superdesk.config.ID_FIELD)
        query = {
            "query": {
                "filtered": {
                    "filter": {
                        "term": {
                            "destination_groups": str(doc_id)
                        }
                    }
                }
            }
        }

        request = ParsedRequest()
        request.args = {'source': json.dumps(query)}
        archive_content = get_resource_service('archive') \
            .get(req=request, lookup=None)

        if archive_content and archive_content.count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Destination Group is referenced by items.')

        dest_groups = self.get(req=None, lookup={'destination_groups': doc_id})
        if dest_groups and dest_groups.count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Destination Group is referenced by other Destination Group/s.')

        dest_groups = get_resource_service('routing_schemes') \
            .get(req=None,
                 lookup={'$or': [
                     {'rules.actions.fetch.destination_groups': doc_id},
                     {'rules.actions.publish.destination_groups': doc_id}
                 ]})

        if dest_groups and dest_groups.count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Destination Group is referenced by Routing Scheme/s.')

    def __validate_self_referenced(self, dest_group_id, dest_groups):
        if dest_groups:
            if self.__is_self_referenced(dest_group_id, dest_groups):
                raise SuperdeskApiError.badRequestError(
                    message='Circular dependency in Destination Group.')

    def __is_self_referenced(self, dest_group_id, dest_groups):
        dest_groups = dest_groups or []

        if dest_group_id in dest_groups:
            return True

        for id in dest_groups:
            group = self.find_one(req=None, _id=id)
            referenced_groups = group.get('destination_groups', [])
            if referenced_groups:
                return self.__is_self_referenced(dest_group_id, referenced_groups)

        return False
