# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


def validate(item, **kwargs):
    """Checks if item has take_key value"""

    # validation
    if not item.get('anpa_take_key', '').strip():
        raise KeyError('Take key cannot be empty!')

    return item

name = 'take_key_validator'
label = 'validate take key'
shortcut = 'v'
callback = validate
