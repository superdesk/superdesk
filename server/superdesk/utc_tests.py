# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from datetime import datetime, timedelta
from superdesk.tests import TestCase
from superdesk.utc import get_date, utcnow, get_expiry_date
from pytz import utc, timezone # flake8: noqa
from nose.tools import assert_raises


class UTCTestCase(TestCase):

    def test_get_date(self):
        self.assertIsInstance(get_date('2012-12-12'), datetime)
        self.assertIsInstance(get_date(datetime.now()), datetime)
        self.assertIsNone(get_date(None))

    def test_utcnow(self):
        self.assertIsInstance(utcnow(), datetime)
        date1 = get_date(datetime.now(tz=utc))
        date2 = utcnow()
        self.assertEqual(date1.year, date2.year)
        self.assertEqual(date1.month, date2.month)
        self.assertEqual(date1.day, date2.day)
        self.assertEqual(date1.hour, date2.hour)
        self.assertEqual(date1.minute, date2.minute)
        self.assertEqual(date1.second, date2.second)

    def test_get_expiry_date(self):
        self.assertIsInstance(get_expiry_date(minutes=60), datetime)
        date1 = utcnow() + timedelta(minutes=60)
        date2 = get_expiry_date(minutes=60)
        self.assertEqual(date1.year, date2.year)
        self.assertEqual(date1.month, date2.month)
        self.assertEqual(date1.day, date2.day)
        self.assertEqual(date1.hour, date2.hour)
        self.assertEqual(date1.minute, date2.minute)
        self.assertEqual(date1.second, date2.second)

    def test_get_expiry_date_with_offset(self):
        offset = utcnow() + timedelta(minutes=10)
        date1 = offset + timedelta(minutes=5)
        date2 = get_expiry_date(minutes=5, offset=offset)
        self.assertEqual(date1.year, date2.year)
        self.assertEqual(date1.month, date2.month)
        self.assertEqual(date1.day, date2.day)
        self.assertEqual(date1.hour, date2.hour)
        self.assertEqual(date1.minute, date2.minute)
        self.assertEqual(date1.second, date2.second)

    def test_get_expiry_date_bad_offset_raises_error(self):
        with assert_raises(TypeError) as error_context:
            offset = '01.02.2013 13:30'
            get_expiry_date(minutes=5, offset=offset)
