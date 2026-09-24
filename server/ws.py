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

import logging
from settings import WS_HOST, WS_PORT, LOG_CONFIG_FILE, BROKER_URL
from superdesk.ws import create_server
from superdesk.logging import configure_logging, configure_graylog
from superdesk import default_settings

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    config = {"WS_HOST": WS_HOST, "WS_PORT": WS_PORT, "BROKER_URL": BROKER_URL}
    configure_logging(LOG_CONFIG_FILE)
    configure_graylog(
        {
            key: getattr(default_settings, key)
            for key in ("GRAYLOG_HOST", "GRAYLOG_PORT", "GRAYLOG_FACILITY", "GRAYLOG_LEVEL")
        }
    )
    create_server(config)
