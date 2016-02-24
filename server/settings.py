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


APPLICATION_NAME = 'Superdesk'

MACROS_MODULE = 'superdesk.macros'

NEWSML_PROVIDER_ID = 'pressassociation.com'
ORGANIZATION_NAME = 'Press Association'
ORGANIZATION_NAME_ABBREVIATION = 'PA'

KEYWORDS_PROVIDER = 'Alchemy'
KEYWORDS_BASE_URL = 'http://access.alchemyapi.com/calls'
KEYWORDS_KEY_API = os.environ.get('KEYWORDS_KEY_API', 'ea87a0a0a219d55492ffa706dc878ee03aadc4c7')

INIT_DATA_PATH = 'data'

INSTALLED_APPS = [
    'apps.auth',
    'superdesk.roles',
    'superdesk.users',
    'apps.auth.db',

    'superdesk.upload',
    'superdesk.sequences',
    'superdesk.notification',
    'superdesk.activity',
    'superdesk.vocabularies',
    'apps.comments',

    'superdesk.io',
    'superdesk.io.feeding_services',
    'superdesk.io.feed_parsers',
    'superdesk.io.subjectcodes',
    'superdesk.io.iptc',
    'apps.io',
    'apps.io.feeding_services',
    'superdesk.publish',
    'superdesk.commands',
    'superdesk.locators.locators',

    'apps.auth',
    'apps.archive',
    'apps.stages',
    'apps.desks',
    'apps.planning',
    'apps.coverages',
    'apps.tasks',
    'apps.preferences',
    'apps.spikes',
    'apps.groups',
    'apps.prepopulate',
    'apps.legal_archive',
    'apps.search',
    'apps.saved_searches',
    'apps.privilege',
    'apps.rules',
    'apps.highlights',
    'apps.publish',
    'apps.publish.formatters',
    'apps.content_filters',
    'apps.content_types',
    'apps.dictionaries',
    'apps.duplication',
    'apps.spellcheck',
    'apps.templates',
    'apps.archived',
    'apps.validators',
    'apps.validate',
    'apps.workspace',
    'apps.macros',
    'apps.archive_broadcast',
    'apps.search_providers',
    'apps.feature_preview',
    'apps.workqueue',
    'apps.picture_crop',

    'superdesk.io.subjectcodes',
    'apps.archive_broadcast',

    'apps.keywords',
    'apps.content_types',
    'apps.picture_crop',

    'pa.topics',
    'pa.pa_img',
]
