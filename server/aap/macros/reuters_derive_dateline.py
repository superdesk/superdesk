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
from bs4 import BeautifulSoup
import logging
from apps.archive.common import format_dateline_to_locmmmddsrc
from superdesk.utc import get_date
from superdesk.metadata.item import BYLINE

logger = logging.getLogger(__name__)


def reuters_derive_dateline(item, **kwargs):
    """
    It seems that most locations injected into the item by the parser are Bangalor
    This function looks for a dateline in the article body an uses that.
    :param items:
    :return:
    """
    try:
        html = item.get('body_html')
        if html:
            soup = BeautifulSoup(html, "html.parser")
            pars = soup.findAll('p')
            if len(pars) >= 2:
                if BYLINE in item and item.get(BYLINE) in pars[0].get_text():
                    first = pars[1].get_text()
                else:
                    first = pars[0].get_text()
                city, source, the_rest = first.partition(' (Reuters) - ')
                if source:
                    # sometimes the city is followed by a comma and either a date or a state
                    city = city.split(',')[0]
                    if any(char.isdigit() for char in city):
                        return
                    cities = find_cities()
                    located = [c for c in cities if c['city'].lower() == city.lower()]
                    # if not dateline we create one
                    if 'dateline' not in item:
                        item['dateline'] = {}
                    # there is already a dateline that is not Bangalore don't do anything just return
                    elif 'located' in item['dateline'] and 'BANGALORE' != item['dateline']['located'].get(
                            'city').upper():
                        return

                    item['dateline']['located'] = located[0] if len(located) > 0 else {'city_code': city,
                                                                                       'city': city,
                                                                                       'tz': 'UTC',
                                                                                       'dateline': 'city'}
                    item['dateline']['source'] = item.get('original_source', 'Reuters')
                    item['dateline']['text'] = format_dateline_to_locmmmddsrc(item['dateline']['located'],
                                                                              get_date(item['firstcreated']),
                                                                              source=item.get('original_source',
                                                                                              'Reuters'))

        return item
    except:
        logging.exception('Reuters dateline macro exception')


name = 'Derive dateline from article text for Reuters'
callback = reuters_derive_dateline
access_type = 'backend'
action_type = 'direct'
