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
HECTARE_SYMBOL = 'ha'


def convert(acres, precision=0):
    """
    Converts from acres to square m or to hectares
    :param acres: Acres value in string
    :return: square m or to hectares value in string, and the symbol
    """
    acre_to_sqm_rate = Decimal(4046.86)
    symbol = SQUARE_METER_SYMBOL
    acres_list = acres.split('-')
    square_meter_list = [Decimal(a) * acre_to_sqm_rate for a in acres_list]

    if any(s for s in square_meter_list if s > Decimal(10000)):
        # if the value is greater than 10000 then convert it to hectares
        square_meter_list = [unit_base.format_converted((s / Decimal(10000)), precision=1) for s in square_meter_list]
        symbol = HECTARE_SYMBOL
    else:
        square_meter_list = [unit_base.format_converted(s, precision=precision) for s in square_meter_list]

    return '-'.join(square_meter_list), symbol


def acre_to_metric(item, **kwargs):
    """Converts acre values to metric"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))((ac)|([aA]cres?))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'acre_to_metric'
label = 'Area acres to metric'
callback = acre_to_metric
access_type = 'frontend'
action_type = 'interactive'
