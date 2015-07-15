# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from collections import namedtuple
import json
import logging
from settings import MAX_VALUE_OF_PUBLISH_SEQUENCE
from superdesk.celery_app import update_key, set_key
from superdesk import get_resource_service
from eve.utils import ParsedRequest
from superdesk.utils import ListCursor
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError

logger = logging.getLogger(__name__)

subscriber_types = ['broadcast', 'digital', 'wire']
SUBSCRIBER_TYPES = namedtuple('SUBSCRIBER_TYPES', ['BROADCAST', 'DIGITAL', 'WIRE'])(*subscriber_types)


class SubscribersResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True
        },
        'media_type': {
            'type': 'string'
        },
        'geo_restrictions': {
            'type': 'string',
            'nullable': True
        },
        'subscriber_type': {
            'type': 'string',
            'allowed': subscriber_types,
            'required': True
        },
        'sequence_num_settings': {
            'type': 'dict',
            'schema': {
                'min': {'type': 'integer'},
                'max': {'type': 'integer'}
            },
            'required': True
        },
        'email': {
            'type': 'email',
            'empty': False,
            'required': True
        },
        'is_active': {
            'type': 'boolean',
            'default': True
        },
        'critical_errors': {
            'type': 'dict',
            'keyschema': {
                'type': 'boolean'
            }
        },
        'last_closed': {
            'type': 'dict',
            'schema': {
                'closed_at': {'type': 'datetime'},
                'closed_by': Resource.rel('users', nullable=True),
                'message': {'type': 'string'}
            }
        },
        'destinations': {
            'type': 'list',
            'required': True,
            "minlength": 1,
            'schema': {
                'type': 'dict',
                'schema': {
                    'name': {'type': 'string', 'required': True, 'empty': False},
                    'format': {'type': 'string', 'required': True},
                    'delivery_type': {'type': 'string', 'required': True},
                    'config': {'type': 'dict'}
                }
            }
        },
        'publish_filter': {
            'type': 'dict',
            'schema': {
                'filter_id': Resource.rel('publish_filters', nullable=True),
                'filter_type': {
                    'type': 'string',
                    'allowed': ['blocking', 'permitting'],
                    'default': 'blocking'
                }
            }
        },
        'global_filters': {
            'type': 'dict',
            'keyschema': {
                'type': 'boolean'
            }
        }
    }

    datasource = {'default_sort': [('_created', -1)]}

    item_methods = ['GET', 'PATCH', 'PUT']

    privileges = {'POST': 'subscribers', 'PATCH': 'subscribers'}


class SubscribersService(BaseService):
    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        if req.args and req.args.get('filter_condition'):
            filter_condition = json.loads(req.args.get('filter_condition'))
            return ListCursor(self._get_subscribers_by_filter_condition(filter_condition))
        return super().get(req=req, lookup=lookup)

    def on_create(self, docs):
        for doc in docs:
            self._validate_seq_num_settings(doc)

    def on_update(self, updates, original):
        self._validate_seq_num_settings(updates)

    def _get_subscribers_by_filter_condition(self, filter_condition):
        req = ParsedRequest()
        all_subscribers = list(super().get(req=req, lookup=None))
        selected_subscribers = {}

        filter_condition_service = get_resource_service('filter_conditions')
        publish_filter_service = get_resource_service('publish_filters')
        existing_filter_conditions = filter_condition_service._check_similar(filter_condition)
        for fc in existing_filter_conditions:
            existing_publish_filters = publish_filter_service._get_publish_filters_by_filter_condition(fc['_id'])
            for pf in existing_publish_filters:
                if pf.get('is_global', False):
                    for s in all_subscribers:
                        if any(gf for gf in s.get('global_filters', []) if str(s['_id']) in gf):
                            selected_subscribers[s['_id']] = s
                else:
                    for s in all_subscribers:
                        if s.get('publish_filter') and \
                            'filter_id' in s['publish_filter'] and \
                                s['publish_filter']['filter_id'] == pf['_id']:
                            selected_subscribers[s['_id']] = s

        return list(selected_subscribers.values())

    def _validate_seq_num_settings(self, subscriber):
        """
        Validates the 'sequence_num_settings' property if present in subscriber. Below are the validation rules:
            1.  If min value is present then it should be greater than 0
            2.  If min is present and max value isn't available then it's defaulted to MAX_VALUE_OF_PUBLISH_SEQUENCE

        :return: True if validation succeeds otherwise return False.
        """

        if subscriber.get('sequence_num_settings'):
            min = subscriber.get('sequence_num_settings').get('min', 1)
            max = subscriber.get('sequence_num_settings').get('max', MAX_VALUE_OF_PUBLISH_SEQUENCE)

            if min <= 0:
                raise SuperdeskApiError.badRequestError(payload={"sequence_num_settings.min": 1},
                                                        message="Value of Minimum in Sequence Number Settings should "
                                                                "be greater than 0")

            if min >= max:
                raise SuperdeskApiError.badRequestError(payload={"sequence_num_settings.min": 1},
                                                        message="Value of Minimum in Sequence Number Settings should "
                                                                "be less than the value of Maximum")

            del subscriber['sequence_num_settings']
            subscriber['sequence_num_settings'] = {"min": min, "max": max}

        return True

    def generate_sequence_number(self, subscriber):
        """
        Generates Published Sequence Number for the passed subscriber
        """

        assert (subscriber is not None), "Subscriber can't be null"

        sequence_key_name = "{subscriber_name}_subscriber_seq".format(subscriber_name=subscriber.get('name')).lower()
        sequence_number = update_key(sequence_key_name, flag=True)

        max_seq_number = MAX_VALUE_OF_PUBLISH_SEQUENCE

        if subscriber.get('sequence_num_settings'):
            if sequence_number == 0 or sequence_number == 1:
                sequence_number = subscriber['sequence_num_settings']['min']
                set_key(sequence_key_name, value=sequence_number)

            max_seq_number = subscriber['sequence_num_settings']['max']

        if sequence_number == max_seq_number:
            set_key(sequence_key_name)

        return sequence_number
