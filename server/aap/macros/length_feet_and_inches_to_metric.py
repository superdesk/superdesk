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
from . import unit_base
from decimal import Decimal


def convert(feet, inches):
    """
    Converts from feet and inches to cm or m
    If feet contains '-' then inches won't have '-'
    If inches contains '-' then feet value will be 0
    :param feet: Feet value in string
    :param inches: Inch value in string
    :return: cm or m value in string, and the symbol as 'm' or 'cm'
    """
    foot_to_cm_rate = Decimal(30.48)
    inch_to_cm_rate = Decimal(2.54)
    total_centimeters = []
    symbol = 'cm'

    if '-' in feet:
        feet_list = feet.split('-')
        total_centimeters = [(Decimal(m) * foot_to_cm_rate) + (Decimal(inches) * inch_to_cm_rate) for m in feet_list]
    elif '-' in inches:
        inches_list = inches.split('-')
        total_centimeters = [(Decimal(i) * inch_to_cm_rate) for i in inches_list]
    else:
        # no multi values
        total_centimeters = [(Decimal(feet) * foot_to_cm_rate) + (Decimal(inches) * inch_to_cm_rate)]

    if any(c for c in total_centimeters if c > Decimal(100)):
        # if the value is greater than 100 then convert it to meter
        total_centimeters = [unit_base.format_converted((c / Decimal(100)), precision=2) for c in total_centimeters]
        symbol = 'm'
    else:
        total_centimeters = [unit_base.format_converted(c, precision=2) for c in total_centimeters]

    return '-'.join(total_centimeters), symbol


def do_conversion(item, converter, formatter, search_param):
    """ Performs the conversion """
    diff = {}

    # Group indexes
    match_index = 0  # Index of complete match i.e. 5' 10"
    value_index = 1  # Index of the value: contains feet if feet is in the match else inches if there's no feet
    feet_symbol_index = 7  # Index of feet symbol ', ft, feet, foot
    inches_with_feet_value_index = 8  # When there is a feet and inch value matched together
    inches_symbol_index = 5  # Index of inches symbol ", in, inch(es)

    def convert(match):
        match_item = match.group(match_index).strip()
        from_value = match.group(value_index)
        inches_from_value = '0'
        feet_symbol = match.group(feet_symbol_index)
        inches_symbol = match.group(inches_symbol_index)
        multi_values = '-' in from_value and from_value[-1:] != '-'

        if match_item and from_value:
            if feet_symbol:
                # check if any inches matched
                inches_from_value = match.group(inches_with_feet_value_index) or '0'
            elif inches_symbol:
                # no feet matching
                inches_from_value = from_value
                from_value = '0'
            else:
                return {}

            if not multi_values:
                from_value = re.sub(r'[^\d.]', '', from_value)
                inches_from_value = re.sub(r'[^\d.]', '', inches_from_value)
            to_value, symbol = converter(from_value, inches_from_value)
            diff.setdefault(match_item.strip(), formatter(match_item.strip(), to_value, symbol))
            return diff[match_item]

    for field in macro_replacement_fields:
        if item.get(field, None):
            item[field] = re.sub(search_param, convert, item[field])

    return (item, diff)


def feet_inches_to_metric(item, **kwargs):
    """Converts distance values from feet and inches to metric"""

    regex = r'(\d+-?,?\.?\d*)((\s*)|(-))(((\'|ft\.?|[fF]eet|[fF]oot)\s?(\d+)?\s?("|in)?)|(\"|[iI]nches|[iI]nch|in))'
    return do_conversion(item, convert, unit_base.format_output, regex)


name = 'feet_inches_to_metric'
label = 'Length feet-inches to metric'
callback = feet_inches_to_metric
access_type = 'frontend'
action_type = 'interactive'
