# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from test_factory import SuperdeskTestCase
from flask import render_template_string


class ConvertDatetimeFiltersTest(SuperdeskTestCase):

    def test_convert_datetime_utc_no_format(self):
        template_string = '{{ item.versioncreated | format_datetime("Australia/Sydney")}}'
        item = {'versioncreated': '2015-01-01T22:54:53+0000'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '2015-01-02 09:54:53+11:00')

    def test_convert_datetime_local_time_no_format(self):
        template_string = '{{ item.versioncreated | format_datetime("Australia/Sydney")}}'
        item = {'versioncreated': '2015-01-01T22:54:53+05:30'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '2015-01-02 04:24:53+11:00')

    def test_convert_datetime_utc_format(self):
        template_string = '{{ item.versioncreated | format_datetime(timezone_string="Australia/Sydney", ' \
                          'date_format="%Y-%m-%d")}}'
        item = {'versioncreated': '2015-01-01T22:54:53+0000'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '2015-01-02')

    def test_convert_datetime_invalid_date(self):
        template_string = '{{ item.versioncreated | format_datetime("Australia/Sydney", "%Y-%m-%d")}}'
        item = {'versioncreated': 'test string'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '')

    def test_convert_datetime_invalid_timezone(self):
        template_string = '{{ item.versioncreated | format_datetime("australia/sydney", "%Y-%m-%d")}}'
        item = {'versioncreated': 'test string'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '')

    def test_convert_datetime_utc_default_timezone(self):
        template_string = '{{ item.versioncreated | format_datetime()}}'
        item = {'versioncreated': '2015-01-01T22:54:53+0000'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '2015-01-01 23:54:53+01:00')

    def test_convert_datetime_local_time_default_timezone(self):
        template_string = '{{ item.versioncreated | format_datetime()}}'
        item = {'versioncreated': '2015-01-01T22:54:53+05:30'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '2015-01-01 18:24:53+01:00')

    def test_convert_datetime_utc_timezone_format(self):
        template_string = '{{ item.versioncreated | format_datetime("Australia/Sydney", "%d %b %Y %H:%S %Z")}}'
        item = {'versioncreated': '2015-01-01T22:54:53+0000'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '02 Jan 2015 09:53 AEDT')

    def test_convert_datetime_utc_timezone_format(self):
        template_string = '{{ item.versioncreated | format_datetime("Australia/Sydney", "%d %b %Y %H:%S %Z")}}'
        item = {'versioncreated': '2015-06-01T22:54:53+0000'}
        result = render_template_string(template_string, item=item)
        self.assertEqual(result, '02 Jun 2015 08:53 AEST')
