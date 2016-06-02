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

KILOMETER_SYMBOL = 'km'


def convert(miles, **kwargs):
    """
    Converts from miles to kilometers
    :param miles: Miles value in string
    :return: Kilometers value in string
    """
    miles_to_km_rate = Decimal(1.609344)
    miles_list = miles.split('-')
    kilometers = [unit_base.format_converted((Decimal(m) * miles_to_km_rate), precision=1) for m in miles_list]
    return '-'.join(kilometers), KILOMETER_SYMBOL


def miles_to_metric(item, **kwargs):
    """Converts distance values from miles to metric"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))((mi)|([mM]iles?))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'miles_to_metric'
label = 'Length miles to kilometers'
callback = miles_to_metric
access_type = 'frontend'
action_type = 'interactive'
