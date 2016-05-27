# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
import superdesk
from superdesk.io.iptc import subject_codes
from superdesk.locators.locators import find_cities
from apps.archive.common import format_dateline_to_locmmmddsrc
from superdesk.utc import get_date

logger = logging.getLogger(__name__)


def noise11_derive_metadata(item, **kwargs):
    """
    By definition anyhting from NOISE11 will be entertainment so set the category, subject and dateline
    appropriately
    :param item:
    :param kwargs:
    :return:
    """
    try:
        if 'anpa_category' not in item:
            category_map = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')
            if category_map:
                map_entry = next((code for code in category_map['items'] if code['qcode'] == 'e' and code['is_active']),
                                 None)
                item['anpa_category'] = [{'qcode': 'e', 'name': map_entry['name']}]

        if 'subject' not in item:
            qcode = '01000000'
            item['subject'] = [{'qcode': qcode, 'name': subject_codes[qcode]}]

        cities = find_cities(country_code='AU', state_code='NSW')
        located = [c for c in cities if c['city'].lower() == 'sydney']

        if located and 'dateline' not in item:
            item['dateline'] = {'date': item['firstcreated'], 'located': located[0]}
        item['dateline']['source'] = item['source']
        item['dateline']['text'] = format_dateline_to_locmmmddsrc(located[0], get_date(item['firstcreated']),
                                                                  source=item['source'])

        return item
    except Exception as ex:
        logger.exception(ex)


name = 'Derive metadata for Noise11'
callback = noise11_derive_metadata
access_type = 'backend'
action_type = 'direct'
