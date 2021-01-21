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
from flask import json
from pathlib import Path
from distutils.util import strtobool


def env(variable, fallback_value=None):
    env_value = os.environ.get(variable, '')
    if len(env_value) == 0:
        return fallback_value
    else:
        if env_value == "__EMPTY__":
            return ''
        else:
            return env_value


ABS_PATH = str(Path(__file__).resolve().parent)

init_data = Path(ABS_PATH) / 'data'
if init_data.exists():
    INIT_DATA_PATH = init_data

INSTALLED_APPS = [
    'apps.languages',
    'ansa.analysis',
    'ansa.search',
    'ansa.parser',
    'ansa.subjects',
    'ansa.formatters',
    'ansa.routing',
    'ansa.stage_auto_publishing',
    'ansa.update_signal',
    'ansa.validate',
    'ansa.save_iptc',
    'ansa.extra',
    'ansa.remove_expired_media',
    'ansa.archive_manage',
    'ansa',

    'planning',
]


RENDITIONS = {
    'picture': {
        'thumbnail': {'width': 220, 'height': 120},
        'viewImage': {'width': 640, 'height': 640},
        'baseImage': {'width': 1400, 'height': 1400},
    },
    'avatar': {
        'thumbnail': {'width': 60, 'height': 60},
        'viewImage': {'width': 200, 'height': 200},
    }
}

WS_HOST = env('WSHOST', '0.0.0.0')
WS_PORT = env('WSPORT', '5100')

LOG_CONFIG_FILE = env('LOG_CONFIG_FILE', 'logging_config.yml')

REDIS_URL = env('REDIS_URL', 'redis://localhost:6379')
if env('REDIS_PORT'):
    REDIS_URL = env('REDIS_PORT').replace('tcp:', 'redis:')
BROKER_URL = env('CELERY_BROKER_URL', REDIS_URL)

NO_TAKES = True

ANSA_ANALYSIS_URL = env('ANSA_EXTRACTION_SERVICE', 'http://172.20.14.51:8080/extractionservice/')
ANSA_TRANSLATION_URL = env('ANSA_TRANSLATION_URL', 'http://172.20.14.84:82/tr2.php')

DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES = 'ANSA'
ORGANIZATION_NAME = 'Agenzia Nazionale Stampa Associata'
ORGANIZATION_NAME_ABBREVIATION = 'ANSA'
NEWSML_PROVIDER_ID = 'ANSA'

LANGUAGES = [
    {'language': 'it', 'label': 'Italiano', 'source': True, 'destination': True},
    {'language': 'en', 'label': 'English', 'source': True, 'destination': True},
    {'language': 'es', 'label': 'Español', 'source': True, 'destination': True},
    {'language': 'pt', 'label': 'Português', 'source': True, 'destination': True},
    {'language': 'de', 'label': 'Deutsch', 'source': True, 'destination': True},
    {'language': 'ar', 'label': 'Arabic', 'source': True, 'destination': True},
]

DEFAULT_LANGUAGE = 'it'

MACROS_MODULE = 'ansa.macros'

LEGAL_ARCHIVE = True

ANSA_PHOTO_API = env('ANSA_PHOTO_API', 'http://172.20.14.67:8080/portaleimmagini/api/')

CONTENT_EXPIRY_MINUTES = 0
PUBLISHED_CONTENT_EXPIRY_MINUTES = 60 * 24 * 30
AUDIT_EXPIRY_MINUTES = PUBLISHED_CONTENT_EXPIRY_MINUTES
CONTENT_API_EXPIRY_DAYS = 15

with open(os.path.join(os.path.dirname(__file__), 'picture-profile.json')) as profile_json:
    picture_profile = json.load(profile_json)

with open(os.path.join(os.path.dirname(__file__), 'package-profile.json')) as profile_json:
    package_profile = json.load(profile_json)

EDITOR = {
    "picture": picture_profile['editor'],
    "audio": picture_profile['editor'],
    "video": picture_profile['editor'],
    "composite": package_profile['editor'],
}

SCHEMA = {
    "picture": picture_profile['schema'],
    "audio": picture_profile['schema'],
    "video": picture_profile['schema'],
    "composite": package_profile['schema'],
}


upload_required = bool(strtobool(env('ANSA_VALIDATE_UPLOAD', 'false')))
VALIDATOR_MEDIA_METADATA = {
    "headline": {"required": upload_required},
    "description_text": {"required": upload_required},
    "PhotoCategories": {"required": upload_required},
    "language": {"required": upload_required},
    "city": {"required": upload_required},
    "byline": {"required": upload_required},
    "coauthor": {"required": upload_required},

    # keep these to make them visible in editor
    "alt_text": {"required": False},
    "copyrightholder": {"required": False},
    "usageterms": {"required": False},
    "copyrightnotice": {"required": False},
}

VALIDATE_MEDIA_METADATA_ON_PUBLISH = False


GEONAMES_USERNAME = env('GEONAMES_USERNAME', 'superdesk_dev')
GEONAMES_FEATURE_CLASSES = ['P']
GEONAMES_SEARCH_STYLE = 'full'

ANSA_VFS = env('ANSA_VFS', 'http://172.20.14.95:8080/')

KILL_TEMPLATE_NULL_FIELDS = []

PUBLISH_ASSOCIATED_ITEMS = bool(strtobool(env('PUBLISH_ASSOCIATED_ITEMS', 'false')))

ELASTICSEARCH_FORCE_REFRESH = False
ELASTICSEARCH_AUTO_AGGREGATIONS = False

ELASTIC_DEFAULT_SIZE = 200

PUBLISH_NOT_QUEUED_ERROR = False

AUTO_PUBLISH_UPDATE_IPTC = bool(strtobool(env('AUTO_PUBLISH_UPDATE_IPTC', 'false')))

FILE_INGEST_OLD_CONTENT_MINUTES = 1

WORKFLOW_ALLOW_DUPLICATE_NON_MEMBERS = True

FULL_SIGN_OFF = True

PRIORITY_TO_PROFILE_MAPPING = {
    '2': 'News B',
    '4': 'News Compact',
}

HEADLINE_MAXLENGTH = 64
