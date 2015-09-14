
import unittest
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
