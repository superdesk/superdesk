import unittest
from ansa.macros.text_to_lowercase import lowercase_macro


class LowercaseMacro(unittest.TestCase):

    def test_lowercase_macro(self):
        item = {'body_html': '<p>TeSt bOdy</p>', 'title': '<p>tEst tiTle</p>'}
        lowercase_macro(item)
        self.assertEqual(item.get('body_html'), '<p>test body</p>')
        self.assertEqual(item.get('title'), '<p>test title</p>')
