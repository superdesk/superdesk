
import unittest
from .currency import usd_to_aud
from .currency_usd_to_cad import usd_to_cad


class CurrencyTestCase(unittest.TestCase):

    def test_usd_to_aud(self):
        item = {'body_html': '$100'}
        res = usd_to_aud(item)
        aud = float(res['body_html'][3:])
        self.assertGreater(aud, 100)  # if this fails, check first the currency ;)

    def test_usd_to_cad(self):
        item = {'body_html': '$100'}
        res = usd_to_cad(item)
        cad = float(res['body_html'][3:])
        self.assertGreater(cad, 100)  # if this fails, check first the currency ;)
