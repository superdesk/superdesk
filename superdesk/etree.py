# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import xml.etree.ElementTree as etree  # noqa
from xml.etree.ElementTree import ParseError  # noqa


def get_text_word_count(text):
    """Get word count for given plain text.

    :param text: text string
    """
    return len(text.split())


def get_word_count(html):
    """Get word count for given html.

    :param html: html string to count
    """
    try:
        root = etree.fromstringlist('<doc>{0}</doc>'.format(html))
        text = etree.tostring(root, encoding='unicode', method='text')
        return get_text_word_count(text)
    except ParseError:
        return get_text_word_count(html)
