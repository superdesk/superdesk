# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from decimal import Decimal
from . import unit_base

CUBIC_METER_SYMBOL = 'cubic meter'
CUBIC_CENTIMETER_SYMBOL = 'cubic centimeter'


def convert(cubic_inches, precision=1):
    """
    Converts from cubic inch to cubic m or cubic cm
    :param cubic_inches: Cubic inch value in string
    :return: cubic m/cm value in string, and the symbol
    """
    ci_to_ccm_rate = Decimal(16.3871)
    symbol = CUBIC_CENTIMETER_SYMBOL
    cubic_inches_list = cubic_inches.split('-')
    cubic_centimeter_list = [Decimal(a) * ci_to_ccm_rate for a in cubic_inches_list]

    if any(s for s in cubic_centimeter_list if s > Decimal(100000)):
        # if the value is greater than 100000 then convert it to cubic meters
        cubic_centimeter_list = [unit_base.format_converted((s / Decimal(1000000)), precision=1)
                                 for s in cubic_centimeter_list]
        symbol = CUBIC_METER_SYMBOL
    else:
        cubic_centimeter_list = [unit_base.format_converted(s, precision=precision) for s in cubic_centimeter_list]

    return '-'.join(cubic_centimeter_list), symbol


def cubic_inches_to_metric(item, **kwargs):
    """Converts cubic inch values to metric"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))((cu\.?\s*-?in)|(cb\.?\s*-?in)|([cC]ubic\s*-?([iI]nches|[iI]nch|in)))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'cubic_inches_to_metric'
label = 'Volume cubic inches to metric'
callback = cubic_inches_to_metric
access_type = 'frontend'
action_type = 'interactive'
