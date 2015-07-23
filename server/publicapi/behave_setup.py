# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os
import unittest
import elasticsearch
from publicapi import get_app
from settings import ELASTICSEARCH_URL
from eve_elastic import get_es, get_indices


TEST_DBNAME = 'sptests'


def get_test_settings():
    test_settings = {}
    test_settings['ELASTICSEARCH_URL'] = ELASTICSEARCH_URL
    test_settings['ELASTICSEARCH_INDEX'] = TEST_DBNAME
    test_settings['MONGO_DBNAME'] = TEST_DBNAME
    test_settings['MONGO_URI'] = 'mongodb://localhost/%s' % TEST_DBNAME
    test_settings['DEBUG'] = True
    test_settings['TESTING'] = True
    test_settings['SUPERDESK_TESTING'] = True
    test_settings['CONTENT_EXPIRY_MINUTES'] = 99
    test_settings['SUPERDESK_PUBLICAPI_TESTING'] = True

    return test_settings


def drop_elastic(app):
    with app.app_context():
        try:
            es = get_es(app.config['ELASTICSEARCH_URL'])
            get_indices(es).delete(app.config['ELASTICSEARCH_INDEX'])
        except elasticsearch.exceptions.NotFoundError:
            pass


def drop_mongo(app):
    with app.test_request_context():
        try:
            app.data.mongo.pymongo().cx.drop_database(app.config['MONGO_DBNAME'])
        except AttributeError:
            pass


def setup(context=None, config=None):
    app_config = get_test_settings()
    if config:
        app_config.update(config)

    app = get_app(app_config)
    drop_elastic(app)
    drop_mongo(app)

    # create index again after dropping it
    app.data.elastic.init_app(app)

    if context:
        context.app = app
        context.client = app.test_client()


def set_placeholder(context, name, value):
    old_p = getattr(context, 'placeholders', None)
    if not old_p:
        context.placeholders = dict()
    context.placeholders[name] = value


def get_prefixed_url(current_app, endpoint):
    if endpoint.startswith('http://'):
        return endpoint

    endpoint = endpoint if endpoint.startswith('/') else ('/' + endpoint)
    url = current_app.config['URL_PREFIX'] + endpoint
    return url


class TestCase(unittest.TestCase):
    def setUp(self):
        setup(self)

    def get_fixture_path(self, filename):
        rootpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(rootpath, 'features', 'steps', 'fixtures', filename)
