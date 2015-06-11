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
    """Updates the abstract field"""

    if not item.get('headline', '').strip():
        raise KeyError('Headline cannot be empty!')


name = 'validate_headline'
label = 'Validate Headline'
shortcut = 'w'
callback = validate
desks = ['POLITICS']
