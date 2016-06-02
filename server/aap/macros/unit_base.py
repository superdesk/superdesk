# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import re
from . import macro_replacement_fields
from decimal import Decimal


def format_converted(converted_value, precision):
    if converted_value > Decimal(1000):
        precision = 0

    if converted_value < Decimal(1) and precision == 0:
        precision = 2

    rounded = round(converted_value, precision)
    if rounded == Decimal(0):
        precision += 1
        rounded = round(converted_value, precision)

    return '{0:,}'.format(round(converted_value, precision))


def format_output(original, converted, symbol):
    """ Returns the replacement string for the given original value """
    return '{} ({} {})'.format(original, converted, symbol)


def do_conversion(item, converter, formatter, search_param, match_index, value_index):
    """
    Performs the conversion
    :param item: story
    :param converter: function to perform conversion
    :param formatter: function to do string formatting
    :param search_param: search parameter to locate the original value.  It should
    be a valid regular expression pattern, and not just an arbitrary string.
    :param match_index: int index of groups used in matching string
    :param value_index: int index of groups used in converting the value
    :return: modified story
    """
    diff = {}

    def convert(match):
        match_item = match.group(match_index)
        from_value = match.group(value_index)
        multi_values = '-' in from_value and from_value[-1:] != '-'
        precision = 0

        if match_item and from_value:
            if not multi_values:
                from_value = re.sub(r'[^\d.]', '', from_value)
                precision = abs(Decimal(from_value).as_tuple().exponent)
            to_value, symbol = converter(from_value, precision=precision)
            diff.setdefault(match_item, formatter(match_item, to_value, symbol))
            return diff[match_item]

    for field in macro_replacement_fields:
        if item.get(field, None):
            item[field] = re.sub(search_param, convert, item[field])

    return (item, diff)
