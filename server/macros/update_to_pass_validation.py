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
import logging
from apps.archive.common import format_dateline_to_locmmmddsrc
from superdesk.utc import get_date

logger = logging.getLogger(__name__)


def update_to_pass_validation(item, **kwargs):
    """
    This is a test macro that does what is required to ensure that a text item will pass publication validation.
    It is intended to be used to test auto publishing, that is publishing directly from ingest.
    At the moment virtually all content received from Reuters fails validation.
    :param item:
    :param kwargs:
    :return:
    """
    try:
        item['slugline'] = item['slugline'][:24] if len(item['slugline']) > 24 else item['slugline']
        item['headline'] = item['headline'][:64] if len(item['headline']) > 64 else item['headline']
        if 'dateline' not in item:
            cities = find_cities(country_code='AU', state_code='NSW')
            located = [c for c in cities if c['city'].lower() == 'sydney']
            if located:
                item['dateline'] = {'date': item['firstcreated'], 'located': located[0]}
            item['dateline']['source'] = item['source']
            item['dateline']['text'] = format_dateline_to_locmmmddsrc(located[0], get_date(item['firstcreated']),
                                                                      source=item['source'])
        return item
    except:
        logging.exception('Test update to pass validation macro exception')

name = 'update to pass validation'
label = 'Update to pass validation'
shortcut = '$'
callback = update_to_pass_validation
