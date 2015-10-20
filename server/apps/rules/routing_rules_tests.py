
import unittest
from unittest import mock

from copy import deepcopy
from datetime import datetime, timedelta
from .routing_rules import Weekdays


class WeekdaysTestCase(unittest.TestCase):

    def test_is_valid_schedule(self):
        self.assertTrue(Weekdays.is_valid_schedule(['MON', 'TUE']))
        self.assertFalse(Weekdays.is_valid_schedule(['MON', 'SRC']))

    def test_is_scheduled(self):
        now = datetime.now()
        day = now.strftime('%A')[:3]

        self.assertFalse(Weekdays.is_scheduled_day(now, []))
        self.assertTrue(Weekdays.is_scheduled_day(now, [day]))
        self.assertFalse(Weekdays.is_scheduled_day(now + timedelta(days=1), [day]))

    def test_weekday_dayname(self):
        now = datetime.now()
        day = now.strftime('%A')[:3].upper()
        self.assertEqual(day, Weekdays.dayname(now))


class RoutingRuleSchemeServiceTest(unittest.TestCase):
    """Base class for RoutingRuleSchemeService tests."""

    def setUp(self):
        try:
            from .routing_rules import RoutingRuleSchemeService
        except ImportError:
            # a missing class should result in a failed test, not in an error
            # that prevents all the tests in the module from even being run
            self.fail(
                "Could not import class under test "
                "(RoutingRuleSchemeService).")
        else:
            self.instance = RoutingRuleSchemeService()


@mock.patch(
    'apps.rules.routing_rules'
    '.RoutingRuleSchemeService._validate_routing_scheme')
@mock.patch(
    'apps.rules.routing_rules'
    '.RoutingRuleSchemeService._check_if_rule_name_is_unique')
class OnCreateMethodTestCase(RoutingRuleSchemeServiceTest):
    """Tests for the on_create() method."""

    def test_does_not_modify_semantically_non_empty_schedules(self, *mocks):
        routing_schemes = [{
            'name': 'scheme_1',
            'rules': [{
                'name': 'rule_1',
                'schedule': {
                    'day_of_week': ['MON'],
                    'hour_of_day_from': '0800',
                    'hour_of_day_to': '1800',
                    'time_zone': 'UTC'
                }
            }]
        }]
        original_scheme = deepcopy(routing_schemes[0])
        self.instance.on_create(routing_schemes)
        self.assertEqual(routing_schemes[0], original_scheme)

    def test_does_not_modify_empty_schedules(self, *mocks):
        routing_schemes = [{
            'name': 'scheme_1',
            'rules': [{
                'name': 'rule_1',
                'schedule': None
            }]
        }]
        original_scheme = deepcopy(routing_schemes[0])
        self.instance.on_create(routing_schemes)
        self.assertEqual(routing_schemes[0], original_scheme)

    def test_sets_semantically_empty_schedules_to_none(self, *mocks):
        routing_schemes = [{
            'name': 'scheme_1',
            'rules': [{
                'name': 'rule_1',
                'schedule': {'time_zone': 'UTC'}  # effectively empty schedule
            }]
        }]

        expected_scheme = deepcopy(routing_schemes[0])
        expected_scheme['rules'][0]['schedule'] = None

        self.instance.on_create(routing_schemes)

        self.assertEqual(routing_schemes[0], expected_scheme)


@mock.patch(
    'apps.rules.routing_rules'
    '.RoutingRuleSchemeService._validate_routing_scheme')
@mock.patch(
    'apps.rules.routing_rules'
    '.RoutingRuleSchemeService._check_if_rule_name_is_unique')
class OnUpdateMethodTestCase(RoutingRuleSchemeServiceTest):
    """Tests for the on_update() method."""

    def test_does_not_modify_semantically_non_empty_schedules(self, *mocks):
        routing_scheme = {
            'name': 'scheme_1',
            'rules': [{
                'name': 'rule_1',
                'schedule': {
                    'day_of_week': ['MON'],
                    'hour_of_day_from': '0800',
                    'hour_of_day_to': '1800',
                    'time_zone': 'UTC'
                }
            }]
        }
        original_scheme = deepcopy(routing_scheme)
        self.instance.on_update(routing_scheme, {})
        self.assertEqual(routing_scheme, original_scheme)

    def test_does_not_modify_empty_schedules(self, *mocks):
        routing_scheme = {
            'name': 'scheme_1',
            'rules': [{
                'name': 'rule_1',
                'schedule': None
            }]
        }
        original_scheme = deepcopy(routing_scheme)
        self.instance.on_update(routing_scheme, {})
        self.assertEqual(routing_scheme, original_scheme)

    def test_sets_semantically_empty_schedules_to_none(self, *mocks):
        routing_scheme = {
            'name': 'scheme_1',
            'rules': [{
                'name': 'rule_1',
                'schedule': {'time_zone': 'UTC'}  # effectively empty schedule
            }]
        }

        expected_scheme = deepcopy(routing_scheme)
        expected_scheme['rules'][0]['schedule'] = None

        self.instance.on_update(routing_scheme, {})

        self.assertEqual(routing_scheme, expected_scheme)


class ValidateScheduleMethodTestCase(RoutingRuleSchemeServiceTest):
    """Tests for the _validate_schedule() method."""

    def setUp(self):
        super().setUp()

        self.schedule = {
            'day_of_week': ['WED', 'FRI']
        }

    @mock.patch(
        'apps.rules.routing_rules.all_timezones_set',
        {'Foo/Bar', 'Foo/Baz', 'Here/There'}
    )
    def test_raises_error_on_unknown_time_zone(self):
        from superdesk.errors import SuperdeskApiError

        self.schedule['time_zone'] = 'Invalid/Zone'

        with self.assertRaises(SuperdeskApiError) as context:
            self.instance._validate_schedule(self.schedule)

        # also check the error message
        msg = context.exception.message
        msg = msg.lower() if msg else ''
        self.assertIn('time zone', msg)
        self.assertIn('invalid/zone', msg)

    def test_allows_empty_end_time(self):
        self.schedule['hour_of_day_from'] = '1030'
        self.schedule['hour_of_day_to'] = ''

        try:
            self.instance._validate_schedule(self.schedule)
        except Exception as ex:
            self.fail(
                "Unexpected exception on empty hour_of_day_to: {}".format(ex)
            )


class GetScheduledRoutingRulesMethodTestCase(RoutingRuleSchemeServiceTest):
    """Tests for the _get_scheduled_routing_rules() method."""

    def test_returns_only_the_rules_scheduled_at_current_time(self):
        rules = [{
            'name': 'rule_1',
            'schedule': {
                'day_of_week': ['SAT'],
                'hour_of_day_from': '0100',
                'hour_of_day_to': '2300',
                'time_zone': 'UTC',
            }
        }, {
            'name': 'rule_2',
            'schedule': {
                'day_of_week': ['MON', 'TUE', 'WED'],
                'hour_of_day_from': '2100',
                'hour_of_day_to': '2200',
                'time_zone': 'UTC',
            }
        }, {
            'name': 'rule_3',
            'schedule': {
                'day_of_week': ['TUE'],
                'hour_of_day_from': '2200',
                'hour_of_day_to': '2300',
                'time_zone': 'UTC',
            }
        }]

        now = datetime(2015, 8, 18, 21, 30)  # Tuesday

        result = self.instance._get_scheduled_routing_rules(rules, now)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], rules[1])

    def test_takes_rule_time_zone_into_account(self):
        rules = [{
            'name': 'rule_berlin',
            'schedule': {
                'day_of_week': ['TUE'],
                'hour_of_day_from': '1400',
                'hour_of_day_to': '1500',
                'time_zone': 'Europe/Berlin',  # UTC +01:00/+02:00
            }
        }, {
            'name': 'rule_singapore',
            'schedule': {
                'day_of_week': ['TUE'],
                'hour_of_day_from': '2200',
                'hour_of_day_to': '2300',
                'time_zone': 'Asia/Singapore',  # always UTC +08:00
            }
        }]

        now = datetime(2015, 9, 15, 14, 30)  # Tuesday

        result = self.instance._get_scheduled_routing_rules(rules, now)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], rules[1])

    def test_assumes_utc_time_zone_if_none_set(self):
        rules = [{
            'name': 'rule_berlin',
            'schedule': {
                'day_of_week': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'],
                'hour_of_day_from': '1450',
                'hour_of_day_to': '1455',
                'time_zone': None,
            }
        }]

        now = datetime(2015, 9, 15, 14, 52)  # Tuesday

        result = self.instance._get_scheduled_routing_rules(rules, now)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], rules[0])

    def test_assumes_from_the_start_of_the_day_if_start_time_not_set(self):
        rules = [{
            'name': 'rule_berlin',
            'schedule': {
                'day_of_week': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'],
                'hour_of_day_from': None,
                'hour_of_day_to': '2030',
                'time_zone': 'UTC',
            }
        }]
        now = datetime(2015, 9, 15, 0, 0, 0, 0)  # Tuesday

        result = self.instance._get_scheduled_routing_rules(rules, now)

        self.assertEqual(result, rules)

    def test_assumes_until_the_end_of_the_day_if_end_time_not_set(self):
        rules = [{
            'name': 'rule_berlin',
            'schedule': {
                'day_of_week': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'],
                'hour_of_day_from': '1845',
                'hour_of_day_to': None,
                'time_zone': 'UTC',
            }
        }]
        now = datetime(2015, 9, 15, 23, 59, 59, 999999)  # Tuesday

        result = self.instance._get_scheduled_routing_rules(rules, now)

        self.assertEqual(result, rules)
