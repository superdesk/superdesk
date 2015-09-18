
import unittest
from datetime import datetime
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE
from .content_templates import get_next_run, Weekdays, get_item_from_template


class TemplatesTestCase(unittest.TestCase):

    def setUp(self):
        # now is today at 09:05:03
        self.now = datetime.now().replace(hour=9, minute=5, second=3)
        self.weekdays = [day.name for day in Weekdays]

    def get_delta(self, create_at, weekdays):
        next_run = get_next_run({'day_of_week': weekdays, 'create_at': create_at, 'is_active': True}, self.now)
        return next_run - self.now.replace(second=0)

    def test_inactive_schedule(self):
        self.assertEqual(None, get_next_run({'is_active': False, 'day_of_week': self.weekdays, 'create_at': '0915'}))

    def test_next_run_same_day_later(self):
        delta = self.get_delta('0908', self.weekdays)
        self.assertEqual(delta.days, 0)
        self.assertEqual(delta.seconds, 180)

    def test_next_run_next_day(self):
        delta = self.get_delta('0903', self.weekdays)
        self.assertEqual(delta.days, 0)
        self.assertEqual(delta.seconds, 3600 * 24 - 120)

    def test_next_run_next_week(self):
        delta = self.get_delta('0903', [self.now.strftime('%a').upper()])
        self.assertEqual(delta.days, 6)

    def test_next_run_now(self):
        delta = self.get_delta('0905', self.weekdays)
        self.assertEqual(delta.days, 1)

    def test_get_item_from_template(self):
        template = {'_id': 'foo', 'name': 'test', 'headline': 'Foo',
                    'template_desk': 'sports', 'template_stage': 'schedule'}
        item = get_item_from_template(template)
        self.assertNotIn('_id', item)
        self.assertEqual('foo', item.get('template'))
        self.assertEqual('Foo', item.get('headline'))
        self.assertEqual(CONTENT_STATE.SUBMITTED, item.get(ITEM_STATE))
        self.assertEqual({'desk': 'sports', 'stage': 'schedule'}, item.get('task'))
