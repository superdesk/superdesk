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
from eve.utils import date_to_str
from apps.archive import init_app
from superdesk.utc import get_expiry_date, utcnow
from apps.archive.commands import RemoveExpiredSpikeContent
from apps.archive import ArchiveService
from nose.tools import assert_raises
from superdesk.errors import SuperdeskApiError
from datetime import datetime, timedelta


class RemoveSpikedContentTestCase(TestCase):

    def setUp(self):
        super().setUp()

        with self.app.app_context():
            self.app.data.insert('archive', [{'expiry': get_expiry_date(-10), 'state': 'spiked'}])
            self.app.data.insert('archive', [{'expiry': get_expiry_date(0), 'state': 'spiked'}])
            self.app.data.insert('archive', [{'expiry': get_expiry_date(10), 'state': 'spiked'}])
            self.app.data.insert('archive', [{'expiry': get_expiry_date(20), 'state': 'spiked'}])
            self.app.data.insert('archive', [{'expiry': get_expiry_date(30), 'state': 'spiked'}])
            self.app.data.insert('archive', [{'expiry': None, 'state': 'spiked'}])
            self.app.data.insert('archive', [{'unique_id': 97, 'state': 'spiked'}])
            init_app(self.app)

    def test_query_getting_expired_content(self):
        with self.app.app_context():
            now = date_to_str(utcnow())
            expiredItems = RemoveExpiredSpikeContent().get_expired_items(now)
            self.assertEquals(2, expiredItems.count())


class ArchiveTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test_validate_schedule(self):
        date_without_time = datetime.strptime('Jun 1 2005', '%b %d %Y')
        time_without_date = datetime.strptime('1:33PM', '%I:%M%p')
        date_in_past = utcnow() + timedelta(hours=-2)
        date_in_future = utcnow() + timedelta(hours=2)

        ArchiveService().validate_schedule(date_in_future)

        with assert_raises(SuperdeskApiError):
            ArchiveService().validate_schedule("2015-04-27T10:53:48+00:00")
            ArchiveService().validate_schedule(date_without_time)
            ArchiveService().validate_schedule(time_without_date)
            ArchiveService().validate_schedule(date_in_past)
