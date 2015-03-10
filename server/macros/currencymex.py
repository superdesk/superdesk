
import re
import requests

from superdesk import macros


MEX_TO_AUD = 1.99  # backup


def get_rate():
    """Get MEX to AUD rate."""
    try:
        r = requests.get('http://rate-exchange.appspot.com/currency?from=MEX&to=AUD', timeout=5)
        return float(r.json()['rate'])
    except Exception:
        return MEX_TO_AUD


def mex_to_aud(item, **kwargs):
    """Convert MEX to AUD."""

    rate = get_rate()

    def convert(match):
        usd = float(match.group(1))
        aud = rate * usd
        return '$%d' % aud

    item['body_html'] = re.sub('\$([0-9]+)', convert, item['body_html'])
    return item


macros.register(
    name='mex_to_aud',
    label='Convert MEX to AUD',
    shortcut='c',
    callback=mex_to_aud,
    desks=['POLITICS']
)
