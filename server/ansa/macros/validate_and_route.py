# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2020 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from .desk_routing import routing
from .validate_headline import callback as validate_headline


def callback(item, **kwargs):
    item = validate_headline(item, **kwargs)
    item = routing(item, **kwargs)
    return item


name = 'validate-headline-desk-routing'
label = 'Validate Headline and Desk Routing'
access_type = 'backend'
action_type = 'direct'
