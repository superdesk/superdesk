
from superdesk.tests import TestCase
from .item_spike import get_unspike_updates, IS_SPIKED, EXPIRY


class SpikeTestCase(TestCase):

    def test_unspike_my_content(self):
        with self.app.app_context():
            item = {'guid': 'test'}
            updates = get_unspike_updates(item)
            self.assertIsNone(updates[IS_SPIKED])
            self.assertIsNone(updates[EXPIRY])

    def test_unspike_workflow_item(self):
        with self.app.app_context():
            desks = self.app.data.insert('desks', [{'incoming_stage': 'foo'}])
            item = {'guid': 'test', 'task': {
                'user': 'baz',
                'desk': str(desks[0]),
                'stage': 'bar',
            }}
            updates = get_unspike_updates(item)
            self.assertEqual('foo', updates['task']['stage'])
