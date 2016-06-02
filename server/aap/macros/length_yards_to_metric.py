# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from . import unit_base
from decimal import Decimal

METERS_SYMBOL = 'meters'


def convert(yards, precision=0):
    """
    Converts from yards to meters
    :param yards: Yards value in string
    :param precision: number of decimal points (int)
    :return: Meters value in string
    """
    yard_to_meter_rate = Decimal(0.9144)
    yards_list = yards.split('-')
    meters = [unit_base.format_converted((Decimal(y) * yard_to_meter_rate), precision) for y in yards_list]
    return '-'.join(meters), METERS_SYMBOL


def yards_to_metric(item, **kwargs):
    """Converts distance values from yard to meters"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))((yd)|([yY]ards?))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'yards_to_metric'
label = 'Length yards to meters'
callback = yards_to_metric
access_type = 'frontend'
action_type = 'interactive'
