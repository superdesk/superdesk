#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import settings
from superdesk.factory import get_app as superdesk_app


def get_app():
    media_storage = None
    if getattr(settings, 'AMAZON_CONTAINER_NAME'):
        from superdesk.storage.amazon.amazon_media_storage import AmazonMediaStorage
        media_storage = AmazonMediaStorage

    app = superdesk_app(settings, media_storage)
    return app
