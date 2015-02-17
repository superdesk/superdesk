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
from superdesk.errors import SuperdeskApiError


logger = logging.getLogger(__name__)


class RoutingRuleSchemeResource(Resource):
    """
    Resource class for 'routing_schemes' endpoint
    """

    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True,
            'minlength': 1
        },
        'rules': {
            'type': 'list',
            'schema': {
                'name': {
                    'type': 'string'
                },
                'filter': {
                    'type': 'dict'
                },
                'actions': {
                    'type': 'dict',
                    'schema': {
                        'fetch': {
                            'type': 'list',
                            'schema': {
                                'desk': Resource.rel('desks', True),
                                'stage': Resource.rel('stages', True)
                            }
                        },
                        'publish': {
                            'type': 'list',
                            'schema': {
                                'desk': Resource.rel('desks', True),
                                'stage': Resource.rel('stages', True)
                            }
                        },
                        'exit': {
                            'type': 'boolean'
                        }
                    }
                },
                'schedule': {
                    'type': 'dict',
                    'schema': {
                        'day_of_week': {
                            'type': 'list',
                            'allowed': ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                        },
                        'hour_of_day_from': {
                            'type': 'integer'
                        },
                        'hour_of_day_to': {
                            'type': 'integer'
                        }
                    }
                }
            }
        }
    }

    datasource = {
        'default_sort': [('name', 1)]
    }

    privileges = {'POST': 'routing_rules', 'DELETE': 'routing_rules', 'PATCH': 'routing_rules'}


class RoutingRuleSchemeService(BaseService):
    """
    Service class for 'routing_schemes' endpoint.
    """

    def on_create(self, docs):
        """
        Overriding to check the below pre-conditions:
            1. A routing scheme must have at least one rule.
            2. Every rule in the routing scheme must have name, filter and at least one action

        Will throw BadRequestError if any of the pre-conditions fail.
        """

        for routing_scheme in docs:
            self.__validate_routing_scheme(routing_scheme)
            self.__check_if_rule_name_is_unique(routing_scheme)

    def on_update(self, updates, original):
        """
        Overriding to check the below pre-conditions:
            1. A routing scheme must have at least one rule.
            2. Every rule in the routing scheme must have name, filter and at least one action

        Will throw BadRequestError if any of the pre-conditions fail.
        """

        self.__validate_routing_scheme(updates)
        self.__check_if_rule_name_is_unique(updates)

    def on_delete(self, doc):
        """
        Overriding to check the below pre-conditions:
            1. A routing scheme shouldn't be associated with an Ingest Provider.

        Will throw BadRequestError if any of the pre-conditions fail.
        """

        if self.backend.find_one('ingest_providers', req=None, routing_scheme=doc['_id']):
            raise SuperdeskApiError.forbiddenError('Routing Scheme is in use')

    def __validate_routing_scheme(self, routing_scheme):
        """
        Validates routing scheme for the below:
            1. A routing scheme must have at least one rule.
            2. Every rule in the routing scheme must have name, filter and at least one action

        Will throw BadRequestError if any of the conditions fail.

        :param routing_scheme:
        """

        routing_rules = routing_scheme.get('rules', [])
        if len(routing_rules) == 0:
            raise SuperdeskApiError.badRequestError(message="A Routing Scheme must have at least one Rule")
        for routing_rule in routing_rules:
            invalid_fields = [field for field in routing_rule.keys()
                              if field not in ('name', 'filter', 'actions', 'schedule')]

            if invalid_fields:
                raise SuperdeskApiError.badRequestError(
                    message="A routing rule has invalid fields %s".format(invalid_fields))

            schedule = routing_rule.get('schedule')
            actions = routing_rule.get('actions')

            if routing_rule.get('name') is None:
                raise SuperdeskApiError.badRequestError(message="A routing rule must have a name")
            elif routing_rule.get('filter') is None or len(routing_rule.get('filter')) == 0:
                raise SuperdeskApiError.badRequestError(message="A routing rule must have a filter")
            elif actions is None or len(actions) == 0 or (actions.get('fetch') is None and actions.get(
                    'publish') is None and actions.get('exit') is None):
                raise SuperdeskApiError.badRequestError(message="A routing rule must have actions")
            elif schedule is not None and (len(schedule) == 0 or (schedule.get('day_of_week') is None or len(
                    schedule.get('day_of_week', [])) == 0)):
                raise SuperdeskApiError.badRequestError(message="Schedule when defined can't be empty.")

    def __check_if_rule_name_is_unique(self, routing_scheme):
        """
        Checks if name of a routing rule is unique or not.
        """

        routing_rules = routing_scheme.get('rules', [])

        for routing_rule in routing_rules:
            rules_with_same_name = [rule for rule in routing_rules if rule.get('name') == routing_rule.get('name')]

            if len(rules_with_same_name) > 1:
                raise SuperdeskApiError.badRequestError("Rule Names must be unique within a scheme")
