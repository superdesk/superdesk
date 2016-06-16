
import unittest
from .vidible import get_vidible_metadata


class VidibleTestCase(unittest.TestCase):

    def test_get_vidible_metadata(self):
        meta = get_vidible_metadata(bcid='538612f0e4b00fbb8e898655', pid='56bb474de4b0568f54a23ed7')
        assert(type(meta) is dict)
        assert(type(meta['height']) is int)
        assert(type(meta['width']) is int)
        assert(meta['mimeType'])
        assert(meta['url'])
        assert(meta['thumbnail'])
