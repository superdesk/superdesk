
import unittest

from .generate import item_to_str


class GenerateTestCase(unittest.TestCase):

    def test_item_to_str_body(self):
        text = item_to_str({'headline': 'test', 'body_html': '<p>one</p><p>two</p>'})
        self.assertEquals('<h2>test</h2>\n<p>one</p>', text)

    def test_item_to_str_no_body(self):
        text = item_to_str({'headline': 'test'})
        self.assertEquals('<h2>test</h2>', text)
