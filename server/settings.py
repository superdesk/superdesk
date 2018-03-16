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

ANSA_ANALYSIS_URL = "http://172.20.14.20:8080/extractionservice/"

DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES = 'ANSA'
ORGANIZATION_NAME = 'Agenzia Nazionale Stampa Associata'
ORGANIZATION_NAME_ABBREVIATION = 'ANSA'
NEWSML_PROVIDER_ID = 'ANSA'

LANGUAGES = [
    {'language': 'it', 'label': 'Italiano', 'source': True, 'destination': False},
    {'language': 'en', 'label': 'English', 'source': True, 'destination': False},
]

DEFAULT_LANGUAGE = 'it'

MACROS_MODULE = 'ansa.macros'

LEGAL_ARCHIVE = True

ANSA_PHOTO_API = env('ANSA_PHOTO_API', 'http://172.20.14.88/ansafoto/portaleimmagini/api/')

CONTENT_EXPIRY_MINUTES = 60 * 24 * 7  # 1w
PUBLISHED_CONTENT_EXPIRY_MINUTES = 60 * 24 * 30
AUDIT_EXPIRY_MINUTES = PUBLISHED_CONTENT_EXPIRY_MINUTES

EDITOR = {
    "picture": {
        "CopyrigthLine": {
            "order": 15
        },
        "authors": {
            "order": 13,
            "sdWidth": "half"
        },
        "subtitle": {
            "order": 3
        },
        "byline": {
            "order": 14,
            "sdWidth": "half"
        },
        "subject": {
            "order": 10,
            "sdWidth": "half"
        },
        "language": {
            "order": 8,
            "sdWidth": "half"
        },
        "headline": {
            "order": 2,
            "formatOptions": [
                "underline",
                "link",
                "bold"
            ]
        },
        "digitator": {
            "order": 6,
            "sdWidth": "half"
        },
        "slugline": {
            "order": 1,
            "sdWidth": "full"
        },
        "place": {
            "order": 7,
            "sdWidth": "half"
        },
        "ednote": {
            "order": 12,
            "sdWidth": "full"
        },
        "keywords": {
            "order": 11,
            "sdWidth": "full"
        },
        "anpa_category": {
            "order": 9,
            "sdWidth": "half"
        },
        "key": {
            "order": 4,
            "sdWidth": "half"
        },
        "date": {
            "order": 5,
            "sdWidth": "half"
        }
    }
}

SCHEMA = {
    "picture": {
        "CopyrigthLine": {
            "required": False,
            "enabled": True,
            "nullable": False,
            "type": "text"
        },
        "authors": {
            "required": True,
            "nullable": False,
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "role": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    },
                    "parent": {
                        "type": "string"
                    }
                }
            }
        },
        "subtitle": {
            "required": False,
            "enabled": True,
            "nullable": True,
            "type": "text"
        },
        "byline": {
            "required": False,
            "nullable": True,
            "type": "string"
        },
        "subject": {
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "name": {},
                    "scheme": {
                        "required": True,
                        "nullable": True,
                        "allowed": [
                            "01"
                        ],
                        "type": "string"
                    },
                    "qcode": {},
                    "parent": {
                        "nullable": True
                    },
                    "service": {
                        "nullable": True
                    }
                }
            },
            "nullable": True,
            "default": [],
            "type": "list",
            "mandatory_in_list": {
                "scheme": {}
            }
        },
        "language": {
            "required": True,
            "enabled": True,
            "nullable": False,
            "type": "string"
        },
        "headline": {
            "required": True,
            "nullable": False,
            "type": "string"
        },
        "digitator": {
            "required": False,
            "enabled": True,
            "nullable": False,
            "type": "text"
        },
        "slugline": {
            "required": True,
            "nullable": False,
            "type": "string"
        },
        "place": {
            "required": False,
            "nullable": True,
            "type": "list"
        },
        "ednote": {
            "required": False,
            "nullable": True,
            "type": "string"
        },
        "keywords": {
            "required": False,
            "enabled": True,
            "nullable": True,
            "type": "list"
        },
        "anpa_category": {
            "required": True,
            "nullable": False,
            "type": "list"
        },
        "date": {
            "required": False,
            "enabled": True,
            "nullable": True,
            "type": "date"
        },
        "key": {
            "required": False,
            "enabled": True,
            "nullable": False,
            "type": "text"
        }
    }
}
