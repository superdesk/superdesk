
import unittest
from .service import words


class WordsTestCase(unittest.TestCase):

    def test_words_parsing(self):
        self.assertEquals(['abc'], words('abc'))
        self.assertEquals(['3d', 'x5'], words('3d 123 x5'))
