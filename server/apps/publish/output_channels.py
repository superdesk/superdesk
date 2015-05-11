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
from apps.archive.common import get_user
from apps.users import is_admin
from settings import MAX_VALUE_OF_PUBLISH_SEQUENCE
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from eve.utils import config

logger = logging.getLogger(__name__)


class OutputChannelsResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True,
        },
        'description': {
            'type': 'string'
        },
        'format': {
            'type': 'string'
        },
        'channel_type': {
            'type': 'string'
        },
        'destinations': {
            'type': 'list',
            'schema': Resource.rel('subscribers', True)
        },
        'is_active': {
            'type': 'boolean',
            'default': True
        },
        'sequence_num_settings': {
            'type': 'dict',
            'schema': {
                'min': {'type': 'integer'},
                'max': {'type': 'integer'}
            }
        }
    }

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'output_channels', 'DELETE': 'output_channels', 'PATCH': 'output_channels'}


class OutputChannelsService(BaseService):

    def on_fetched(self, doc):
        """
        Overriding to take care of existing data in Mongo
        """
        for item in doc[config.ITEMS]:
            if item and 'sequence_num_settings' in item and 'start_from' in item['sequence_num_settings']:
                del item['sequence_num_settings']['start_from']

    def on_create(self, docs):
        for doc in docs:
            self.__is_authorized_to_update_seq_num_settings(doc)
            self.__validate_seq_num_settings(doc)

    def on_update(self, updates, original):
        self.__is_authorized_to_update_seq_num_settings(updates)
        self.__validate_seq_num_settings(updates)

    def on_delete(self, doc):
        lookup = {'output_channels.channel': str(doc.get('_id'))}
        dest_groups = get_resource_service('destination_groups').get(req=None, lookup=lookup)
        if dest_groups and dest_groups.count() > 0:
            raise SuperdeskApiError.preconditionFailedError(
                message='Output Channel is associated with Destination Groups.')

    def find_one(self, req, **lookup):
        """
        Overriding to take care of existing data in Mongo
        """
        item = super().find_one(req, **lookup)

        if item and 'sequence_num_settings' in item and 'start_from' in item['sequence_num_settings']:
            del item['sequence_num_settings']['start_from']

        return item

    def __is_authorized_to_update_seq_num_settings(self, output_channel):
        """
        Checks if the user requested is authorized to modify sequence number settings.
        If unauthorized then exception will be raised.
        """

        user = get_user()
        if 'sequence_num_settings' in output_channel and not is_admin(user) \
                and (user['active_privileges'].get('output_channel_seq_num_settings', 0) == 0):
            raise SuperdeskApiError.forbiddenError("Unauthorized to modify Sequence Number Settings")

    def __validate_seq_num_settings(self, output_channel):
        """
        Validates the 'sequence_num_settings' property if present in output_channel. Below are the validation rules:
            1.  If min value is present then it should be greater than 0
            2.  If min is present and max value isn't available then it's defaulted to MAX_VALUE_OF_PUBLISH_SEQUENCE

        :return: True if validation succeeds otherwise return False.
        """

        if output_channel.get('sequence_num_settings'):
            min = output_channel.get('sequence_num_settings').get('min', 1)
            max = output_channel.get('sequence_num_settings').get('max', MAX_VALUE_OF_PUBLISH_SEQUENCE)

            if min <= 0:
                raise SuperdeskApiError.badRequestError(payload={"sequence_num_settings.min": 1},
                                                        message="Value of Minimum in Sequence Number Settings should "
                                                                "be greater than 0")

            if min >= max:
                raise SuperdeskApiError.badRequestError(payload={"sequence_num_settings.min": 1},
                                                        message="Value of Minimum in Sequence Number Settings should "
                                                                "be less than the value of Maximum")

            del output_channel['sequence_num_settings']
            output_channel['sequence_num_settings'] = {"min": min, "max": max}

        return True
