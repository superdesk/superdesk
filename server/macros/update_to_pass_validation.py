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
import superdesk
from superdesk.metadata.item import CONTENT_TYPE
from apps.publish.content.common import ITEM_PUBLISH

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
        lookup = {'act': ITEM_PUBLISH, 'type': CONTENT_TYPE.TEXT}
        validators = superdesk.get_resource_service('validators').get(req=None, lookup=lookup)
        if validators.count():
            max_slugline_len = validators[0]['schema']['slugline']['maxlength']
            max_headline_len = validators[0]['schema']['headline']['maxlength']
            item['slugline'] = item['slugline'][:max_slugline_len] \
                if len(item['slugline']) > max_slugline_len else item['slugline']
            item['headline'] = item['headline'][:max_headline_len] \
                if len(item['headline']) > max_headline_len else item['headline']
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
