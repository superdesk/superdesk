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

CUBIC_METER_SYMBOL = 'kg'


def convert(pounds, precision=1):
    """
    Converts from pounds to kg
    :param pounds: Pounds value in string
    :return: Kg value in string, and the symbol
    """
    lb_to_kg_rate = Decimal(0.453592)
    symbol = CUBIC_METER_SYMBOL
    pounds_list = pounds.split('-')
    kg_list = [unit_base.format_converted(Decimal(a) * lb_to_kg_rate, precision) for a in pounds_list]
    return '-'.join(kg_list), symbol


def pounds_to_metric(item, **kwargs):
    """Converts pound values to metric"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))((lbs?)|([pP]ounds?))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'pounds_to_metric'
label = 'Weight pounds to metric'
callback = pounds_to_metric
access_type = 'frontend'
action_type = 'interactive'
