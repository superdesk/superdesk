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
from . import currency_base


USD_TO_AUD = 1.40  # backup


def get_rate():
    """Get USD to AUD rate."""
    try:
        return currency_base.get_rate('USD', 'AUD')
    except:
        return USD_TO_AUD


def usd_to_aud(item, **kwargs):
    """Convert USD to AUD."""

    rate = get_rate()
    if os.environ.get('BEHAVE_TESTING'):
        rate = USD_TO_AUD

    return currency_base.do_conversion(item, rate, 'AUD %d', '\$([0-9]+)')


name = 'usd_to_aud'
label = 'Convert USD to AUD'
shortcut = 'c'
callback = usd_to_aud
