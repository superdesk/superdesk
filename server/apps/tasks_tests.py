# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from test_factory import SuperdeskTestCase
from apps.archive.common import get_item_expiry
from app import get_app
from superdesk.utc import get_expiry_date
from apps.tasks import apply_stage_rule, compare_dictionaries
from nose.tools import assert_raises
from superdesk.errors import SuperdeskApiError


class TasksTestCase(SuperdeskTestCase):

    app = None

    def setUp(self):
        app_config = self.get_test_settings()
        self.app = get_app(app_config)

    def get_test_settings(self):
        test_settings = {}
        test_settings['CONTENT_EXPIRY_MINUTES'] = 99
        return test_settings

    def test_get_global_content_expiry(self):
        calculated_minutes = get_item_expiry(self.app, None)
        reference_minutes = get_expiry_date(99)
        self.assertEquals(calculated_minutes.hour, reference_minutes.hour)
        self.assertEquals(calculated_minutes.minute, reference_minutes.minute)

    def test_get_stage_content_expiry(self):
        stage = {"content_expiry": 10}
        calculated_minutes = get_item_expiry(self.app, stage)
        reference_minutes = get_expiry_date(10)
        self.assertEquals(calculated_minutes.hour, reference_minutes.hour)
        self.assertEquals(calculated_minutes.minute, reference_minutes.minute)

    def test_apply_incoming_stage_rule(self):
        doc = {'id': '1', 'body_html': 'Test-1'}
        update = {'anpa_take_key': 'x'}
        stage = {'incoming_macro': 'populate_abstract'}
        with self.app.app_context():
            apply_stage_rule(doc, update, stage, is_incoming=True)
            self.assertEquals(update['abstract'], 'Test-1')

    def test_apply_outgoing_stage_rule(self):
        doc = {'id': '1', 'body_html': 'Test-1'}
        update = {'anpa_take_key': 'x'}
        stage = {'outgoing_macro': 'populate_abstract'}
        with self.app.app_context():
            apply_stage_rule(doc, update, stage, is_incoming=False)
            self.assertEquals(update['abstract'], 'Test-1')

    def test_apply_stage_incoming_validation_rule(self):
        doc = {'id': '1', 'body_html': 'Test-1'}
        update = {'headline': 'x'}
        stage = {'incoming_macro': 'take_key_validator'}
        with self.app.app_context():
            with assert_raises(SuperdeskApiError):
                apply_stage_rule(doc, update, stage, is_incoming=True)

    def test_apply_stage_incoming_validation_rule_passes(self):
        doc = {'id': '1', 'body_html': 'Test-1', 'anpa_take_key': 'a'}
        update = {'headline': 'x'}
        stage = {'incoming_macro': 'take_key_validator'}
        with self.app.app_context():
            apply_stage_rule(doc, update, stage, is_incoming=True)

    def test_apply_stage_incoming_validation_rule_ignored(self):
        doc = {'id': '1', 'body_html': 'Test-1'}
        update = {'headline': 'x'}
        stage = {'outgoing_macro': 'take_key_validator'}
        with self.app.app_context():
            apply_stage_rule(doc, update, stage, is_incoming=True)

    def test_apply_stage_outgoing_validation_rule_ignored(self):
        doc = {'id': '1', 'body_html': 'Test-1'}
        update = {'headline': 'x'}
        stage = {'incoming_macro': 'take_key_validator'}
        with self.app.app_context():
            apply_stage_rule(doc, update, stage, is_incoming=False)

    def test_apply_stage_outgoing_validation_rule(self):
        doc = {'id': '1', 'body_html': 'Test-1'}
        update = {'headline': 'x'}
        stage = {'outgoing_macro': 'take_key_validator'}
        with self.app.app_context():
            with assert_raises(SuperdeskApiError):
                apply_stage_rule(doc, update, stage, is_incoming=False)

    def test_compare_dictionaries(self):
        original = {
            'id': 1,
            'body_html': 'Test-1'
        }

        updates = {
            'body_html': 'Test-2',
            'headline': 'a',
        }

        modified = compare_dictionaries(original, updates)
        self.assertEquals(2, len(modified))
        self.assertTrue('body_html' in modified)
        self.assertTrue('headline' in modified)
