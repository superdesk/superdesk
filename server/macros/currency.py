
import re
import requests

from superdesk import macros


USD_TO_AUD = 1.27  # backup


def get_rate():
    """Get USD to AUD rate."""
    try:
        r = requests.get('http://rate-exchange.appspot.com/currency?from=USD&to=AUD', timeout=5)
        return float(r.json()['rate'])
    except Exception:
        return USD_TO_AUD


def usd_to_aud(item):
    """Converts USD to AUD"""

    rate = get_rate()

    def convert(match):
        usd = float(match.group(1))
        aud = rate * usd
        return '$%d' % aud

    item['body_html'] = re.sub('\$([0-9]+)', convert, item['body_html'])
    return item


macros.register(
    name='usd_to_aud',
    label='Convert USD to AUD',
    shortcut='c',
    callback=usd_to_aud
)
