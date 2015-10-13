
import unittest
from unittest import mock
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
    def test_foo(self):
        from superdesk.errors import SuperdeskApiError

        self.schedule['time_zone'] = 'Invalid/Zone'

        with self.assertRaises(SuperdeskApiError) as context:
            self.instance._validate_schedule(self.schedule)

        # also check the error message
        msg = context.exception.message
        msg = msg.lower() if msg else ''
        self.assertIn('time zone', msg)
        self.assertIn('invalid/zone', msg)
