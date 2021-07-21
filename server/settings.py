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

import os
from pathlib import Path
from superdesk.default_settings import INSTALLED_APPS, strtobool


def env(variable, fallback_value=None):
    env_value = os.environ.get(variable, "")
    if len(env_value) == 0:
        return fallback_value
    else:
        if env_value == "__EMPTY__":
            return ""
        else:
            return env_value


ABS_PATH = str(Path(__file__).resolve().parent)

init_data = Path(ABS_PATH) / "data"
if init_data.exists():
    INIT_DATA_PATH = init_data

INSTALLED_APPS.extend(
    [
        "apps.languages",
        "planning",
    ]
)

PLANNING_EVENT_TEMPLATES_ENABLED = True

RENDITIONS = {
    "picture": {
        "thumbnail": {"width": 220, "height": 120},
        "viewImage": {"width": 640, "height": 640},
        "baseImage": {"width": 1400, "height": 1400},
    },
    "avatar": {
        "thumbnail": {"width": 60, "height": 60},
        "viewImage": {"width": 200, "height": 200},
    },
}

WS_HOST = env("WSHOST", "0.0.0.0")
WS_PORT = env("WSPORT", "5100")

LOG_CONFIG_FILE = env("LOG_CONFIG_FILE", "logging_config.yml")

REDIS_URL = env("REDIS_URL", "redis://localhost:6379")
if env("REDIS_PORT"):
    REDIS_URL = env("REDIS_PORT").replace("tcp:", "redis:")
BROKER_URL = env("CELERY_BROKER_URL", REDIS_URL)

SECRET_KEY = env("SECRET_KEY", "")

# Highcharts Export Server - default settings
ANALYTICS_ENABLE_SCHEDULED_REPORTS = strtobool(env("ANALYTICS_ENABLE_SCHEDULED_REPORTS", "true"))
HIGHCHARTS_SERVER_HOST = env("HIGHCHARTS_SERVER_HOST", "localhost")
HIGHCHARTS_SERVER_PORT = env("HIGHCHARTS_SERVER_PORT", "6060")

NINJS_PLACE_EXTENDED = True
PUBLISH_ASSOCIATED_ITEMS = True

DEFAULT_TIMEZONE = "Europe/Prague"
