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
from . import macro_replacement_fields
from superdesk import get_resource_service


def find_and_replace(item, **kwargs):
    """
    Find and replace words
    :param dict item:
    :param kwargs:
    :return tuple(dict, dict): tuple of modified item and diff of items modified.
    """
    diff = {}

    def do_find_replace(input_string, words_list):
        for word in words_list:
            pattern = r'{}'.format(re.escape(word.get('existing', '')))

            if re.search(pattern, input_string, flags=re.IGNORECASE):
                diff[word.get('existing', '')] = word.get('replacement', '')
                input_string = re.sub(pattern, word.get('replacement', ''), input_string, flags=re.IGNORECASE)

        return input_string

    vocab = get_resource_service('vocabularies').find_one(req=None, _id='replace_words')

    if vocab:
        replace_words_list = vocab.get('items') or []

        if not replace_words_list:
            return (item, diff)

        for field in macro_replacement_fields:
            if not item.get(field, None):
                continue

            item[field] = do_find_replace(item[field], replace_words_list)

    return (item, diff)


name = 'Replace_Words'
label = 'Replace American Words'
shortcut = 'a'
callback = find_and_replace
access_type = 'frontend'
action_type = 'interactive'
