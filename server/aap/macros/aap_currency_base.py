# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import requests
import re
from . import macro_replacement_fields
from decimal import Decimal

RATE_SERVICE = 'http://download.finance.yahoo.com/d/quotes.csv?s={}=X&f=nl1d1'


def to_currency(value, places=2, curr='', sep=',', dp='.', pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


def get_rate(from_currency, to_currency):
    """Get the exchange rate."""
    r = requests.get(RATE_SERVICE.format(from_currency + to_currency), timeout=5)
    return Decimal(r.text.split(',')[1])


def format_output(original, converted):
    """ Returns the replacement string for the given original value """
    if original[-1:].isalpha():
        # If there's 'm' or 'b' at the end of the original carry that across
        converted += original[-1:]
    return '{} ({})'.format(original, converted)


def do_conversion(item, rate, currency, search_param, match_index, value_index):
    """
    Performs the conversion
    :param item: story
    :param rate: exchange rate
    :param currency: currency symbol or prefix to be used in the results
    :param search_param: search parameter to locate the original value.  It should
    be a valid regular expression pattern, and not just an arbitrary string.
    :param match_index: int index of groups used in matching string
    :param value_index: int index of groups used in converting the value
    :return: modified story
    """
    diff = {}

    def convert(match):
        match_item = match.group(match_index)
        value_item = match.group(value_index)
        if match_item and value_item:
            if ')' in match_item and '(' not in match_item:
                # clear any trailing parenthesis
                match_item = re.sub('[)]', '', 'match_item')

            from_value = Decimal(re.sub(r'[^\d.]', '', value_item))
            precision = abs(from_value.as_tuple().exponent)
            to_value = rate * from_value
            converted_value = to_currency(to_value, places=precision, curr=currency)
            diff.setdefault(match_item, format_output(match_item, converted_value))
            return diff[match_item]

    for field in macro_replacement_fields:
        if item.get(field, None):
            item[field] = re.sub(search_param, convert, item[field])

    return (item, diff)
