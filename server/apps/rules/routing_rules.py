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
from enum import Enum
from datetime import datetime
from apps.rules.routing_rule_validator import RoutingRuleValidator
from superdesk import get_resource_service
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError
from eve.utils import config
from superdesk.metadata.item import CONTENT_STATE

logger = logging.getLogger(__name__)


class Weekdays(Enum):
    """Weekdays names we use for scheduling."""

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6

    @classmethod
    def is_valid_schedule(cls, list_of_days):
        """Test if all days in list_of_days are valid day names.

        :param list list_of_days eg. ['mon', 'tue', 'fri']
        """
        return all([day.upper() in cls.__members__ for day in list_of_days])

    @classmethod
    def is_scheduled_day(cls, today, list_of_days):
        """Test if today's weekday is in schedule.

        :param datetime today
        :param list list_of_days
        """
        return today.weekday() in [cls[day.upper()].value for day in list_of_days]


def set_time(current_datetime, timestr=None):
    """Set time of given datetime according to timestr.

    Time format for timestr is `%H%M`, eg. 1014.

    :param datetime current_datetime
    :param string timestr
    """
    if timestr is None:
        timestr = '0000'
    time = datetime.strptime(timestr, '%H%M')
    return current_datetime.replace(hour=time.hour, minute=time.minute)


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
                'type': 'dict',
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
                                    'type': 'dict',
                                    'schema': {
                                        'desk': Resource.rel('desks', True),
                                        'stage': Resource.rel('stages', True),
                                        'macro': {'type': 'string'}
                                    }
                                }
                            },
                            'publish': {
                                'type': 'list',
                                'schema': {
                                    'type': 'dict',
                                    'schema': {
                                        'desk': Resource.rel('desks', True),
                                        'stage': Resource.rel('stages', True),
                                        'macro': {'type': 'string'}
                                    }
                                }
                            },
                            'exit': {
                                'type': 'boolean'
                            },
                            'preserve_desk': {
                                'type': 'boolean'
                            }
                        }
                    },
                    'schedule': {
                        'type': 'dict',
                        'schema': {
                            'day_of_week': {
                                'type': 'list'
                            },
                            'hour_of_day_from': {
                                'type': 'string'
                            },
                            'hour_of_day_to': {
                                'type': 'string'
                            }
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

        if self.backend.find_one('ingest_providers', req=None, routing_scheme=doc[config.ID_FIELD]):
            raise SuperdeskApiError.forbiddenError('Routing scheme is applied to channel(s). It cannot be deleted.')

    def apply_routing_scheme(self, ingest_item, provider, routing_scheme):
        """
        applies routing scheme and applies appropriate action (fetch, publish) to the item
        :param item: ingest item to which routing scheme needs to applied.
        :param provider: provider for which the routing scheme is applied.
        :param routing_scheme: routing scheme.
        """
        rules = routing_scheme.get('rules', [])
        if not rules:
            logger.warning("Routing Scheme % for provider % has no rules configured." %
                           (provider.get('name'), routing_scheme.get('name')))

        for rule in self.__get_scheduled_routing_rules(rules):
            if RoutingRuleValidator().is_valid_rule(ingest_item, rule.get('filter', {})):
                if rule.get('actions', {}).get('preserve_desk', False) and ingest_item.get('task', {}).get('desk'):
                    desk = get_resource_service('desks').find_one(req=None, _id=ingest_item['task']['desk'])
                    self.__fetch(ingest_item, [{'desk': desk[config.ID_FIELD], 'stage': desk['incoming_stage']}])
                    fetch_actions = [f for f in rule.get('actions', {}).get('fetch', [])
                                     if f.get('desk') != ingest_item['task']['desk']]
                else:
                    fetch_actions = rule.get('actions', {}).get('fetch', [])

                self.__fetch(ingest_item, fetch_actions)
                self.__publish(ingest_item, rule.get('actions', {}).get('publish', []))
                if rule.get('actions', {}).get('exit', False):
                    break
            else:
                logger.info("Routing rule %s of Routing Scheme %s for Provider %s did not match for item %s" %
                            (rule.get('name'), routing_scheme.get('name'),
                             provider.get('name'), ingest_item[config.ID_FIELD]))

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
            elif actions is None or len(actions) == 0 or (actions.get('fetch') is None and actions.get(
                    'publish') is None and actions.get('exit') is None):
                raise SuperdeskApiError.badRequestError(message="A routing rule must have actions")
            else:
                self.__validate_schedule(schedule)

    def __validate_schedule(self, schedule):
        if schedule is not None \
                and (len(schedule) == 0
                     or (schedule.get('day_of_week') is None
                         or len(schedule.get('day_of_week', [])) == 0)):
            raise SuperdeskApiError.badRequestError(message="Schedule when defined can't be empty.")

        if schedule:
            if not Weekdays.is_valid_schedule(schedule.get('day_of_week', [])):
                raise SuperdeskApiError.badRequestError(message="Invalid values for day of week.")

            if schedule.get('hour_of_day_from') or schedule.get('hour_of_day_to'):
                try:
                    from_time = datetime.strptime(schedule.get('hour_of_day_from'), '%H%M')
                except:
                    raise SuperdeskApiError.badRequestError(message="Invalid value for from time.")

                try:
                    to_time = datetime.strptime(schedule.get('hour_of_day_to'), '%H%M')
                except:
                    raise SuperdeskApiError.badRequestError(message="Invalid value for to time.")

                if from_time > to_time:
                    raise SuperdeskApiError.badRequestError(message="From time should be less than To Time.")

    def __check_if_rule_name_is_unique(self, routing_scheme):
        """
        Checks if name of a routing rule is unique or not.
        """
        routing_rules = routing_scheme.get('rules', [])

        for routing_rule in routing_rules:
            rules_with_same_name = [rule for rule in routing_rules if rule.get('name') == routing_rule.get('name')]

            if len(rules_with_same_name) > 1:
                raise SuperdeskApiError.badRequestError("Rule Names must be unique within a scheme")

    def __get_scheduled_routing_rules(self, rules, current_datetime=datetime.now()):
        """
        Iterates rules list and returns the list of rules that are scheduled.
        """
        scheduled_rules = []
        for rule in rules:
            is_scheduled = True
            schedule = rule.get('schedule', {})
            if schedule:
                from_time = set_time(current_datetime, schedule.get('hour_of_day_from'))
                to_time = set_time(current_datetime, schedule.get('hour_of_day_to'))
                if not (Weekdays.is_scheduled_day(current_datetime, schedule.get('day_of_week', []))
                        and (from_time < current_datetime < to_time)):
                    is_scheduled = False

            if is_scheduled:
                scheduled_rules.append(rule)

        return scheduled_rules

    def __fetch(self, ingest_item, destinations):
        """
        Fetch to item to the destinations
        :param item: item to be fetched
        :param destinations: list of desk and stage
        """
        archive_items = []
        for destination in destinations:
            try:
                item_id = get_resource_service('fetch') \
                    .fetch([{config.ID_FIELD: ingest_item[config.ID_FIELD],
                             'desk': str(destination.get('desk')),
                             'stage': str(destination.get('stage')),
                             'state': CONTENT_STATE.ROUTED,
                             'macro': destination.get('macro', None)}])[0]

                archive_items.append(item_id)
            except:
                logger.exception("Failed to fetch item %s to desk %s" % (ingest_item['guid'], destination))

        return archive_items

    def __publish(self, ingest_item, destinations):
        """
        Fetches the item to the desk and then publishes the item.
        :param item: item to be published
        :param destinations: list of desk and stage
        """
        items_to_publish = self.__fetch(ingest_item, destinations)
        for item in items_to_publish:
            try:
                get_resource_service('archive_publish').patch(item, {})
            except:
                logger.exception("Failed to publish item %s." % item)
