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

SQUARE_METER_SYMBOL = 'square meter'
SQUARE_CENTIMETER_SYMBOL = 'square cm'


def convert(square_inch, precision=1):
    """
    Converts from square inch to square m or to hectares
    :param acres: Square inch value in string
    :return: square m or to hectares value in string, and the symbol
    """
    sqi_to_sqm_rate = Decimal(6.4516)
    symbol = SQUARE_CENTIMETER_SYMBOL
    square_inch_list = square_inch.split('-')
    square_meter_list = [Decimal(a) * sqi_to_sqm_rate for a in square_inch_list]

    if any(s for s in square_meter_list if s > Decimal(10000)):
        # if the value is greater than 10000 then convert it to hectares
        square_meter_list = [unit_base.format_converted((s / Decimal(10000)), precision=1) for s in square_meter_list]
        symbol = SQUARE_METER_SYMBOL
    else:
        square_meter_list = [unit_base.format_converted(s, precision=2) for s in square_meter_list]

    return '-'.join(square_meter_list), symbol


def square_inch_to_metric(item, **kwargs):
    """Converts square inch values to metric"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))((sq\.?\s*-?in)|([sS]quare\s*-?(([iI]nch)|([iI]nches)|in)))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'square_inch_to_metric'
label = 'Area square inch to metric'
callback = square_inch_to_metric
access_type = 'frontend'
action_type = 'interactive'
