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

from pathlib import Path
from superdesk.default_settings import strtobool, env

ABS_PATH = str(Path(__file__).resolve().parent)

init_data = Path(ABS_PATH) / "data"
if init_data.exists():
    INIT_DATA_PATH = init_data

INSTALLED_APPS = [
    "apps.languages",
    "planning",
]

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
ANALYTICS_ENABLE_SCHEDULED_REPORTS = strtobool(
    env('ANALYTICS_ENABLE_SCHEDULED_REPORTS', 'true')
)

MACROS_MODULE = env('MACROS_MODULE', 'macros')

HIGHCHARTS_SERVER_HOST = env('HIGHCHARTS_SERVER_HOST', 'localhost')
HIGHCHARTS_SERVER_PORT = env('HIGHCHARTS_SERVER_PORT', '6060')
HIGHCHARTS_LICENSE_ID = env('HIGHCHARTS_LICENSE_ID', '')
HIGHCHARTS_LICENSE_TYPE = 'OEM'
HIGHCHARTS_LICENSEE = 'Sourcefabric Ventures s.r.o.'
HIGHCHARTS_LICENSEE_CONTACT = 'tech@sourcefabric.org'
HIGHCHARTS_LICENSE_CUSTOMER_ID = '2'
HIGHCHARTS_LICENSE_EXPIRY = 'Perpetual'

DEFAULT_LANGUAGE = 'en'
LANGUAGES = [
    {'language': 'en', 'label': 'English', 'source': True, 'destination': True},
    {'language': 'en-GB', 'label': 'English (GB)', 'source': True, 'destination': True},
    {'language': 'fr', 'label': 'French', 'source': True, 'destination': True},
    {'language': 'ar', 'label': 'Arabic', 'source': True, 'destination': True},
    {'language': 'de', 'label': 'German', 'source': True, 'destination': True},
    {'language': 'no', 'label': 'Norwegian', 'source': True, 'destination': True},
    {'language': 'pt-PT', 'label': 'Portugese', 'source': True, 'destination': True},
    {'language': 'pt-BR', 'label': 'Portugese (Brazil)', 'source': True, 'destination': True},
    {'language': 'zh-Hans', 'label': 'Chinese (分类)', 'source': True, 'destination': True},
    {'language': 'dk', 'label': 'Danish', 'source': True, 'destination': True},
    {'language': 'es', 'label': 'Spanish', 'source': True, 'destination': True},
    {'language': 'se', 'label': 'Swedish', 'source': True, 'destination': True},
    {'language': 'cz', 'label': 'Czech', 'source': True, 'destination': True}
]

GENERATE_SHORT_GUID = True

ARCHIVE_AUTOCOMPLETE = True
ARCHIVE_AUTOCOMPLETE_DAYS = 30
KEYWORDS_ADD_MISSING_ON_PUBLISH = True

# publishing of associated and related items
PUBLISH_ASSOCIATED_ITEMS = True

FTP_TIMEOUT = int(env('FTP_TIMEOUT', 10))

PLANNING_EVENT_TEMPLATES_ENABLED = True

PLANNING_AUTO_ASSIGN_TO_WORKFLOW = True

# special characters that are disallowed
DISALLOWED_CHARACTERS = ['!', '$', '%', '&', '"', '(', ')', '*', '+', ',', '.', '/', ':', ';', '<', '=',
                         '>', '?', '@', '[', ']', '\\', '^', '_', '`', '{', '|', '}', '~']

# This value gets injected into NewsML 1.2 and G2 output documents.
NEWSML_PROVIDER_ID = 'sourcefabric.org'
ORGANIZATION_NAME = env('ORGANIZATION_NAME', 'Sourcefabric')
ORGANIZATION_NAME_ABBREVIATION = env('ORGANIZATION_NAME_ABBREVIATION', 'SoFab')

SCHEMA = {
    'picture': {
        'slugline': {'required': False},
        'headline': {'required': False},
        'description_text': {'required': True},
        'byline': {'required': False},
        'copyrightnotice': {'required': False},
        'usageterms': {'required': False},
        'ednote': {'required': False},
    },
    'video': {
        'slugline': {'required': False},
        'headline': {'required': False},
        'description_text': {'required': True},
        'byline': {'required': True},
        'copyrightnotice': {'required': False},
        'usageterms': {'required': False},
        'ednote': {'required': False},
    },
}

# editor for images, video, audio
EDITOR = {
    'picture': {
        'headline': {'order': 1, 'sdWidth': 'full'},
        'description_text': {'order': 2, 'sdWidth': 'full', 'textarea': True},
        'byline': {'order': 3, 'displayOnMediaEditor': True},
        'copyrightnotice': {'order': 4, 'displayOnMediaEditor': True},
        'slugline': {'displayOnMediaEditor': True},
        'ednote': {'displayOnMediaEditor': True},
        'usageterms': {'order': 5, 'displayOnMediaEditor': True},
    },
    'video': {
        'headline': {'order': 1, 'sdWidth': 'full'},
        'description_text': {'order': 2, 'sdWidth': 'full', 'textarea': True},
        'byline': {'order': 3, 'displayOnMediaEditor': True},
        'copyrightnotice': {'order': 4, 'displayOnMediaEditor': True},
        'slugline': {'displayOnMediaEditor': True},
        'ednote': {'displayOnMediaEditor': True},
        'usageterms': {'order': 5, 'displayOnMediaEditor': True},
    },
}

SCHEMA['audio'] = SCHEMA['video']
EDITOR['audio'] = EDITOR['video']


# media required fields for upload
VALIDATOR_MEDIA_METADATA = {
    "slugline": {
        "required": False,
    },
    "headline": {
        "required": False,
    },
    "description_text": {
        "required": True,
    },
    "byline": {
        "required": False,
    },
    "copyrightnotice": {
        "required": False,
    },
}

NINJS_PLACE_EXTENDED = True
PUBLISH_ASSOCIATED_ITEMS = True

DEFAULT_TIMEZONE = "Europe/Prague"

ARCHIVE_AUTOCOMPLETE = True
ARCHIVE_AUTOCOMPLETE_DAYS = 2
ARCHIVE_AUTOCOMPLETE_LIMIT = 2000

# 2: reindex slugline
SCHEMA_VERSION = 2
