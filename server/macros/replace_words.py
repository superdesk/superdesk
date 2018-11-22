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

from superdesk import get_resource_service
from superdesk.macros import macro_replacement_fields


def find_and_replace(item, **kwargs):
    """
    Find and replace words
    :param dict item:
    :param kwargs:
    :return tuple(dict, dict): tuple of modified item and diff of items modified.
    """
    diff = {}

    def repl(new, old):
        """
        Returns a version of the "new" string that matches the case of the "old" string
        :param new:
        :param old:
        :return: a string which is a version of "new" that matches the case of old.
        """
        if old.islower():
            return new.lower()
        elif old.isupper():
            return new.upper()
        else:
            # the old string starts with upper case so we use the title function
            if old[:1].isupper():
                return new.title()
            # it is more complex so try to match it
            else:
                result = ''
                all_upper = True
                for i, c in enumerate(old):
                    if i >= len(new):
                        break
                    if c.isupper():
                        result += new[i].upper()
                    else:
                        result += new[i].lower()
                        all_upper = False
                # append any remaining characters from new
                if all_upper:
                    result += new[i + 1:].upper()
                else:
                    result += new[i + 1:].lower()
                return result

    def do_find_replace(input_string, words_list):
        found_list = {}
        for word in words_list:
            pattern = r'{}'.format(re.escape(word.get('existing', '')))

            while re.search(pattern, input_string, flags=re.IGNORECASE):
                # get the original string from the input
                original = re.search(pattern, input_string, flags=re.IGNORECASE).group(0)
                replacement = repl(word.get('replacement', ''), original)
                if found_list.get(original):
                    break
                diff[original] = replacement
                found_list[original] = replacement
                input_string = input_string.replace(original, replacement)

        return input_string

    vocab = get_resource_service('vocabularies').find_one(req=None, _id='replace_words')

    if vocab:
        replace_words_list = vocab.get('items') or []

        if not replace_words_list:
            return item

        for field in macro_replacement_fields:
            if not item.get(field, None):
                continue

            item[field] = do_find_replace(item[field], replace_words_list)

    return item


name = 'Replace_Words'
label = 'Replace words in the article'
order = 1
shortcut = 'a'
callback = find_and_replace
access_type = 'frontend'
action_type = 'direct'
