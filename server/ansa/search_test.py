
import unittest

from .search import AnsaPictureProvider


class AnsaPictureTestCase(unittest.TestCase):

    def setUp(self):
        self.service = AnsaPictureProvider({})

    def test_find(self):
        items = self.service.find({})
        self.assertEqual(25, len(items))
        item = items[0]
        self.assertIn('headline', item)
        self.assertIn('type', item)
        self.assertIn('versioncreated', item)
        self.assertIn('description_text', item)
        self.assertIn('renditions', item)
