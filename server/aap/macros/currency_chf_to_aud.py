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
from . import aap_currency_base as currency_base
from decimal import Decimal

CHF_TO_AUD = Decimal('1.40')  # backup


def get_rate():
    """Get CHF to AUD rate."""
    try:
        return currency_base.get_rate('CHF', 'AUD')
    except:
        return CHF_TO_AUD


def chf_to_aud(item, **kwargs):
    """Convert CHF to AUD."""

    rate = kwargs.get('rate') or get_rate()
    if os.environ.get('BEHAVE_TESTING'):
        rate = CHF_TO_AUD

    regex = r'((Fr)|(CHF))\s*\-?\s*\(?(((\d{1,3}((\,\d{3})*|\d*))?' \
            r'(\.\d{1,4})?)|((\d{1,3}((\,\d{3})*|\d*))(\.\d{0,4})?))\)?([mb])?'

    return currency_base.do_conversion(item, rate, '$A', regex, match_index=0, value_index=4)


name = 'chf_to_aud'
label = 'Currency CHF to AUD'
callback = chf_to_aud
access_type = 'frontend'
action_type = 'interactive'
