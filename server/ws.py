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


from settings import WS_HOST, WS_PORT, LOG_SERVER_ADDRESS, LOG_SERVER_PORT
from superdesk.ws import create_server


if __name__ == '__main__':
    config = {
        'WS_HOST': WS_HOST,
        'WS_PORT': WS_PORT,
        'LOG_SERVER_ADDRESS': LOG_SERVER_ADDRESS,
        'LOG_SERVER_PORT': LOG_SERVER_PORT
    }
    create_server(config)
