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


def find_and_replace(item, **kwargs):
    """Finds the instances of '$' character and
    replaces with 'AUD ' (with a trailing space)"""

    aud = 'AUD '

    for field in ['body_html', 'body_text', 'abstract', 'headline', 'slugline']:
        if item.get(field, None):
            item[field] = re.sub('[$]', aud, item[field])

    return item

name = 'dollar_AUD_character_replace'
label = '$ -> AUD'
shortcut = '$'
callback = find_and_replace
