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


USD_TO_CAD = 1.3139  # backup


def get_rate():
    """Get USD to CAD rate."""
    try:
        return currency_base.get_rate('USD', 'CAD')
    except:
        return USD_TO_CAD


def usd_to_cad(item, **kwargs):
    """Convert USD to CAD."""

    rate = get_rate()
    if os.environ.get('BEHAVE_TESTING'):
        rate = USD_TO_CAD

    return currency_base.do_conversion(item, rate, 'CAD %d', '\$([0-9]+)')


name = 'usd_to_cad'
label = 'Convert USD to CAD'
shortcut = 'd'
callback = usd_to_cad
