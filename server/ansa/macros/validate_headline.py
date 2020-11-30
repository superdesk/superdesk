# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2020 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from flask import current_app as app, request
from eve.validation import ValidationError


def callback(item, **kwargs):
    try:
        if request and item.get('headline') and len(item['headline']) > app.config['HEADLINE_MAXLENGTH']:
            raise ValidationError("Headline is too long")
    except KeyError:
        return item


name = 'validate-headline'
label = 'Validate Headline'
access_type = 'backend'
action_type = 'direct'
