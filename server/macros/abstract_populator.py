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
from bs4 import BeautifulSoup


def populate(item, **kwargs):
    """Populate the abstract field with the first sentence of the body"""

    # compile the regex
    # p = re.compile('[.!?]')
    p = re.compile('(?i)(?<=[.?!])\\S+(?=[a-z])')

    # get the list of sentences of the body
    if not item.get('body_html', None):
        item['abstract'] = 'No body found to use for abstract...'
    else:
        sentences = p.split(item['body_html'])

        # chop the first sentence to size for abstract (64)
        if sentences and len(sentences) > 0:
            item['abstract'] = BeautifulSoup(sentences[0][:64], "html.parser").text

    return item

name = 'populate_abstract'
label = 'Populate Abstract'
shortcut = 'a'
callback = populate
desks = ['POLITICS']
