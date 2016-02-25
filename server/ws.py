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


from superdesk.ws import create_server
from app import get_app


if __name__ == '__main__':
    app = get_app()

    config = {
        'WS_HOST': app.config['WS_HOST'],
        'WS_PORT': int(app.config['WS_PORT']),
        'LOG_SERVER_ADDRESS': app.config['LOG_SERVER_ADDRESS'],
        'LOG_SERVER_PORT': app.config['LOG_SERVER_PORT']
    }

    create_server(config)
