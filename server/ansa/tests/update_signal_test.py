
import unittest
from ansa.update_signal import handle_item_update


class HandleItemUpdateHeadlineTestCase(unittest.TestCase):

    def test_no_headline(self):
        item = {}
        handle_item_update(None, item)

    def test_first_update(self):
        item = {'headline': 'foo', 'rewrite_sequence': 1}
        handle_item_update(None, item)
        self.assertEqual('foo (2)', item['headline'])

    def test_following_update(self):
        item = {'headline': 'foo (2)', 'rewrite_sequence': 2}
        handle_item_update(None, item)
        self.assertEqual('foo (3)', item['headline'])

    def test_reset_fields_meta(self):
        item = {'headline': 'foo', 'rewrite_sequence': 1, 'fields_meta': {
            'headline': {'draftjsState': {}},
        }}
        handle_item_update(None, item)
        self.assertEqual(None, item['fields_meta']['headline'])
