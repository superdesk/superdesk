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

    # replacements
    if item.get('body_html', None):
        item['body_html'] = re.sub('[$]', aud, item['body_html'])

    if item.get('body_text', None):
        item['body_text'] = re.sub('[$]', aud, item['body_text'])

    if item.get('abstract', None):
        item['abstract'] = re.sub('[$]', aud, item['abstract'])

    if item.get('headline', None):
        item['headline'] = re.sub('[$]', aud, item['headline'])

    if item.get('slugline', None):
        item['slugline'] = re.sub('[$]', aud, item['slugline'])

    return item

name = 'dollar_AUD_character_replace'
label = '$ -> AUD'
shortcut = '$'
callback = find_and_replace
