
import unittest
from datetime import datetime
from .content_templates import get_next_run, WEEKDAYS


class TemplatesTestCase(unittest.TestCase):

    def setUp(self):
        # now is today at 09:05
        self.now = datetime.now().replace(hour=9, minute=5, second=0)

    def get_delta(self, create_at, weekdays):
        next_run = get_next_run({'day_of_week': weekdays, 'create_at': create_at}, self.now)
        return next_run - self.now

    def test_next_run_same_day_later(self):
        delta = self.get_delta('0908', WEEKDAYS)
        self.assertEqual(delta.days, 0)
        self.assertEqual(delta.seconds, 180)

    def test_next_run_next_day(self):
        delta = self.get_delta('0903', WEEKDAYS)
        self.assertEqual(delta.days, 0)
        self.assertEqual(delta.seconds, 3600 * 24 - 120)

    def test_next_run_next_week(self):
        delta = self.get_delta('0903', [self.now.strftime('%a').upper()])
        self.assertEqual(delta.days, 6)
