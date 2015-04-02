# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


def update_fields(item, **kwargs):
    """Updates the abstract field"""

    item['abstract'] = 'Abstract has been updated'
    return item


name = 'update_fields'
label = 'Update Fields'
shortcut = 'w'
callback = update_fields
desks = ['POLITICS']
