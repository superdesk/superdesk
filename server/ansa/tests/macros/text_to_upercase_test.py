import unittest
from ansa.macros.text_to_uppercase import uppercase_macro


class UppercaseMacro(unittest.TestCase):

    def test_uppercase_macro(self):
        item = {'body_html': '<p>TeSt bOdy</p>', 'title': '<p>tEst tiTle</p>'}
        uppercase_macro(item)
        self.assertEqual(item.get('body_html'), '<p>TEST BODY</p>')
        self.assertEqual(item.get('title'), '<p>TEST TITLE</p>')
