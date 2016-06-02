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

SQUARE_KILOMETER_SYMBOL = 'square km'
HECTARE_SYMBOL = 'ha'


def convert(square_miles, precision=1):
    """
    Converts from square miles to square m or to hectares
    :param acres: Square miles value in string
    :return: square m or to hectares value in string, and the symbol
    """
    sqm_to_ha_rate = Decimal(258.999)
    symbol = HECTARE_SYMBOL
    square_miles_list = square_miles.split('-')
    square_meter_list = [Decimal(a) * sqm_to_ha_rate for a in square_miles_list]

    if any(s for s in square_meter_list if s > Decimal(1000)):
        # if the value is greater than 10000 then convert it to hectares
        square_meter_list = [unit_base.format_converted((s / Decimal(100)), precision=1) for s in square_meter_list]
        symbol = SQUARE_KILOMETER_SYMBOL
    else:
        square_meter_list = [unit_base.format_converted(s, precision=precision) for s in square_meter_list]

    return '-'.join(square_meter_list), symbol


def square_mile_to_metric(item, **kwargs):
    """Converts from square miles to metric"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))((sq\.?\s*-?mi)|([sS]quare\s*-?[mM]iles?)|([sS]quare\s*-?mi))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'square_mile_to_metric'
label = 'Area square miles to metric'
callback = square_mile_to_metric
access_type = 'frontend'
action_type = 'interactive'
