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


def convert(cubic_yard, precision=1):
    """
    Converts from cubic yard to cubic m
    :param cubic_yard: Cubic yard value in string
    :return: cubic m value in string, and the symbol
    """
    cy_to_cm_rate = Decimal(0.764555)
    symbol = CUBIC_METER_SYMBOL
    cubic_yard_list = cubic_yard.split('-')
    cubic_meter_list = [unit_base.format_converted(Decimal(a) * cy_to_cm_rate, precision) for a in cubic_yard_list]
    return '-'.join(cubic_meter_list), symbol


def cubic_yard_to_metric(item, **kwargs):
    """Converts cubic yard values to metric"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))((cu\.?\s*-?yds?)|(cb\.?\s*-?yds?)|([cC]ubic\s*-?([yY]ards?|yds?)))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'cubic_yard_to_metric'
label = 'Volume cubic yard to metric'
callback = cubic_yard_to_metric
access_type = 'frontend'
action_type = 'interactive'
