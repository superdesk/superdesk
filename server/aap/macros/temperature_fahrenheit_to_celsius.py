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

CELSIUS_SYMBOL = 'degrees Celsius'


def convert(fahrenheit, precision=0):
    """
    Converts from fahrenheit to celsius with honoring -40 equality
    :param fahrenheit: Fahrenheit value in string
    :param precision: number of decimal points (int)
    :return: Celsius value in string
    """
    def process_fahrenheits(f):
        return unit_base.format_converted((((Decimal(f) + 40) / Decimal(1.8)) - 40), precision)

    fahrenheit_list = fahrenheit.split('-')
    celsius = [process_fahrenheits(f) for f in fahrenheit_list]
    return '-'.join(celsius), CELSIUS_SYMBOL


def fahrenheit_to_celsius(item, **kwargs):
    """Converts temperature values from fahrenheit to celsius"""

    regex = r'(\d+-?\.?\d*)((\s*)|(-))((°?F)|((degrees)?\s*[fF]ahrenheit))\b'
    return unit_base.do_conversion(item, convert, unit_base.format_output, regex, match_index=0, value_index=1)


name = 'fahrenheit_to_celsius'
label = 'Temperature °F to °C'
callback = fahrenheit_to_celsius
access_type = 'frontend'
action_type = 'interactive'
