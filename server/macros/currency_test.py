
import unittest
from .currency import usd_to_aud


class CurrencyTestCase(unittest.TestCase):

    def test_usd_to_aud(self):
        item = {'body_html': '$100'}
        res = usd_to_aud(item)
        aud = float(res['body_html'][1:])
        self.assertGreater(aud, 100)  # if this fails, check first the currency ;)
