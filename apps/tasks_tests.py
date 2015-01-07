# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.tests import TestCase
from apps.tasks import set_expiry
from app import get_app
from superdesk.utc import get_expiry_date


class TasksTestCase(TestCase):

    app = None

    def setUp(self):
        app_config = self.get_test_settings()
        self.app = get_app(app_config)

    def get_test_settings(self):
        test_settings = {}
        test_settings['CONTENT_EXPIRY_MINUTES'] = 99
        return test_settings

    def test_get_global_content_expiry(self):
        calculated_minutes = set_expiry(self.app, None, None)
        reference_minutes = get_expiry_date(99)
        self.assertEquals(calculated_minutes.hour, reference_minutes.hour)
        self.assertEquals(calculated_minutes.minute, reference_minutes.minute)

    def test_get_desk_content_expiry(self):
        desk = {"content_expiry": 50}
        calculated_minutes = set_expiry(self.app, desk, None)
        reference_minutes = get_expiry_date(50)
        self.assertEquals(calculated_minutes.hour, reference_minutes.hour)
        self.assertEquals(calculated_minutes.minute, reference_minutes.minute)

    def test_get_stage_content_expiry(self):
        desk = {"content_expiry": 50}
        stage = {"content_expiry": 10}
        calculated_minutes = set_expiry(self.app, desk, stage)
        reference_minutes = get_expiry_date(10)
        self.assertEquals(calculated_minutes.hour, reference_minutes.hour)
        self.assertEquals(calculated_minutes.minute, reference_minutes.minute)
