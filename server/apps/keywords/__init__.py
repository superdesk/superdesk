# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from apps.keywords.resource import KeywordsResource
from apps.keywords.service import KeywordsService
from apps.keywords.alchemy import AlchemyKeywordsProvider


def init_app(app):
    endpoint_name = 'keywords'
    service = KeywordsService(endpoint_name, backend=superdesk.get_backend())
    if app.config['KEYWORDS_PROVIDER'] == 'Alchemy':
        service.provider = AlchemyKeywordsProvider()
    KeywordsResource(endpoint_name, app=app, service=service)
