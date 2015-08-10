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


USD_TO_CAD = 1.3139  # backup


def get_rate():
    """Get USD to CAD rate."""
    try:
        r = requests.get('http://download.finance.yahoo.com/d/quotes.csv?s=USDCAD=X&f=nl1d1', timeout=5)
        return float(r.text.split(',')[1])
    except Exception:
        return USD_TO_CAD


def usd_to_cad(item, **kwargs):
    """Convert USD to CAD."""

    rate = get_rate()
    if os.environ.get('BEHAVE_TESTING'):
        rate = USD_TO_CAD

    def convert(match):
        usd = float(match.group(1))
        cad = rate * usd
        return 'CAD %d' % cad

    item['body_html'] = re.sub('\$([0-9]+)', convert, item['body_html'])
    return item

name = 'usd_to_cad'
label = 'Convert USD to CAD'
shortcut = 'd'
callback = usd_to_cad
desks = ['SPORTS DESK', 'POLITICS']
