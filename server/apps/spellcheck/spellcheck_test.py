
import unittest

from .spellcheck import norvig_suggest


class SpellcheckTestCase(unittest.TestCase):

    def test_suggestsions(self):

        model = {'foe': 3, 'fox': 5}
        suggestions = norvig_suggest('foo', model)
        self.assertEquals(['fox', 'foe'], suggestions)
