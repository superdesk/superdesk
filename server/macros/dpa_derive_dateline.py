# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.locators.locators import find_cities


def dpa_derive_dateline(item, **kwargs):
    """
    DPA content is recieved in IPTC7901 format, this macro attempts to parse a dateline from the first few lines of
    the item body and populate the dataline location, it also populates the dateline source.
    If a dateline is matched the coresponding string is removed from the article text.
    :param item:
    :param kwargs:
    :return:
    """
    lines = item['body_html'].splitlines()
    if lines:
        # expect the dateline in the first 5 lines, sometimes there is what appears to be a headline preceeding it.
        for line_num in range(0, min(len(lines), 5)):
            city, source, the_rest = lines[line_num].partition(' (dpa) - ')
            # test if we found a candidate and ensure that the city starts the line and is not crazy long
            if source and lines[line_num].find(city) == 0 and len(city) < 20:
                cities = find_cities()
                located = [c for c in cities if c['city'].lower() == city.lower()]
                if 'dateline' not in item:
                    item['dateline'] = {}
                item['dateline']['located'] = located[0] if len(located) > 0 else {'city_code': city, 'city': city,

                                                                                   'tz': 'UTC', 'dateline': 'city'}
                item['dateline']['source'] = 'dpa'
                item['dateline']['text'] = city
                lines[line_num] = lines[line_num].replace(city + source, '')
                item['body_html'] = '\r\n'.join(lines)
                break
    return item


name = 'Derive dateline from article text for DPA'
label = 'DPA dateline derivation'
shortcut = '$'
callback = dpa_derive_dateline
