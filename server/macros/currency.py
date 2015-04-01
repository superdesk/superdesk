# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
import re
import requests


USD_TO_AUD = 1.27  # backup


def get_rate():
    """Get USD to AUD rate."""
    try:
        r = requests.get('http://rate-exchange.appspot.com/currency?from=USD&to=AUD', timeout=5)
        return float(r.json()['rate'])
    except Exception:
        return USD_TO_AUD


def usd_to_aud(item, **kwargs):
    """Convert USD to AUD."""

    rate = get_rate()
    if os.environ.get('BEHAVE_TESTING'):
        rate = USD_TO_AUD

    def convert(match):
        usd = float(match.group(1))
        aud = rate * usd
        return '$%d' % aud

    item['body_html'] = re.sub('\$([0-9]+)', convert, item['body_html'])
    return item

name = 'usd_to_aud'
label = 'Convert USD to AUD'
shortcut = 'c'
callback = usd_to_aud
desks = ['SPORTS DESK', 'POLITICS']
