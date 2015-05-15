# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json

from datetime import date
from eve.utils import ParsedRequest
from publicapi.tests import ApiTestCase
from unittest import mock
from unittest.mock import MagicMock
from werkzeug.datastructures import MultiDict


class ItemsServiceTestCase(ApiTestCase):
    """Base class for the `items` service tests."""

    def _get_target_class(self):
        """Return the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from publicapi.items import ItemsService
        except ImportError:
            self.fail("Could not import class under test (ItemsService).")
        else:
            return ItemsService

    def _make_one(self, *args, **kwargs):
        """Create a new instance of the class under test."""
        return self._get_target_class()(*args, **kwargs)


class CheckRequestParamsMethodTestCase(ItemsServiceTestCase):
    """Tests for the _check_request_params() helper method."""

    def test_does_not_raise_an_error_on_valid_parameters(self):
        request = MagicMock()
        request.args = MultiDict([('sort_by', 'language')])
        instance = self._make_one()

        try:
            instance._check_request_params(request, ('foo', 'sort_by', 'bar'))
        except Exception as ex:
            self.fail("Exception unexpectedly raised ({})".format(ex))

    def test_raises_correct_error_on_unexpected_parameters(self):
        request = MagicMock()
        request.args = MultiDict([('param_x', 'something')])

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance._check_request_params(request, ('foo', 'bar'))

        ex = context.exception
        self.assertEqual(ex.desc, 'Unexpected parameter (param_x)')

    def test_raises_more_descriptive_error_on_filtering_disabled(self):
        request = MagicMock()
        request.args = MultiDict([('q', '{"language": "en"}')])

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance._check_request_params(
                request, whitelist=(), allow_filtering=False)

        ex = context.exception
        self.assertEqual(
            ex.desc,
            'Filtering is not supported when retrieving a single object '
            '(the "q" parameter)'
        )

    def test_raises_correct_error_on_duplicate_parameters(self):
        request = MagicMock()
        request.args = MultiDict([('foo', 'value 1'), ('foo', 'value 2')])

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance._check_request_params(request, whitelist=('foo',))

        ex = context.exception
        self.assertEqual(
            ex.desc, "Multiple values received for parameter (foo)")


fake_super_get = MagicMock(name='fake super().get')


@mock.patch('publicapi.items.service.BaseService.get', fake_super_get)
class GetMethodTestCase(ItemsServiceTestCase):
    """Tests for the get() method."""

    def setUp(self):
        super().setUp()
        fake_super_get.reset_mock()

    @mock.patch('publicapi.items.service.ItemsService._check_request_params')
    def test_correctly_invokes_parameter_validation(self, fake_check_params):
        fake_request = MagicMock()
        fake_request.args = MultiDict()
        lookup = {}

        instance = self._make_one()
        instance.get(fake_request, lookup)

        self.assertTrue(fake_check_params.called)
        args, kwargs = fake_check_params.call_args

        self.assertGreater(len(args), 0)
        self.assertEqual(args[0], fake_request)

        expected_whitelist = sorted(['start_date', 'end_date', 'q'])

        whitelist_arg = kwargs.get('whitelist')
        if whitelist_arg is not None:
            # NOTE: the whitelist argument is converted to a list, because any
            # iterable type is valid, not just lists
            self.assertEqual(sorted(list(whitelist_arg)), expected_whitelist)
        else:
            # whitelist can also be passed as a positional argument
            self.assertGreater(len(args), 1)
            self.assertEqual(sorted(list(args[1])), expected_whitelist)

    def test_invokes_superclass_method_with_given_arguments(self):
        request = MagicMock()
        request.args = MultiDict()
        lookup = {}

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertEqual(len(args), 2)
        self.assertIs(args[0], request)
        self.assertIs(args[1], lookup)

    def test_provides_request_object_to_superclass_if_not_given(self):
        lookup = {}

        instance = self._make_one()
        instance.get(None, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertEqual(len(args), 2)
        self.assertIsInstance(args[0], ParsedRequest)

    def test_sets_query_filter_on_request_object_if_present(self):
        request = MagicMock()
        request.args = MultiDict([('q', '{"language": "de"}')])
        lookup = {}

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)

        query_filter = json.loads(args[0].where)
        self.assertEqual(query_filter.get('language'), 'de')

    def test_raises_correct_error_on_invalid_date_parameter(self):
        request = MagicMock()
        request.args = MultiDict([('start_date', '2015-13-35')])
        lookup = {}

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(
            ex.desc, "Invalid parameter value (start_date)")

    def test_raises_correct_error_if_start_date_greater_than_end_date(self):
        request = MagicMock()
        request.args = MultiDict([
            ('start_date', '2015-02-17'),
            ('end_date', '2015-02-16')
        ])
        lookup = {}

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(
            ex.desc, "Start date must not be greater than end date")

    def test_allows_start_and_end_dates_to_be_equal(self):
        request = MagicMock()
        request.args = MultiDict([
            ('start_date', '2010-01-28'),
            ('end_date', '2010-01-28')
        ])
        lookup = {}
        instance = self._make_one()

        try:
            instance.get(request, lookup)
        except Exception as ex:
            self.fail("Exception unexpectedly raised ({})".format(ex))

    def test_includes_given_date_range_into_query_filter_if_given(self):
        request = MagicMock()
        request.args = MultiDict([
            ('start_date', '2012-08-21'),
            ('end_date', '2012-08-26')
        ])
        lookup = {}

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)

        date_filter = json.loads(args[0].where).get('versioncreated', {})
        expected_filter = {
            '$gte': '2012-08-21',
            '$lte': '2012-08-26'
        }
        self.assertEqual(date_filter, expected_filter)

    @mock.patch('publicapi.items.service.date', wraps=date)
    def test_sets_end_date_to_today_if_not_given(self, fake_date_class):
        request = MagicMock()
        request.args = MultiDict([('start_date', '2012-08-21')])
        lookup = {}

        fake_date_class.today.return_value = date(2014, 7, 15)

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)

        date_filter = json.loads(args[0].where).get('versioncreated', {})
        expected_filter = {
            '$gte': '2012-08-21',
            '$lte': '2014-07-15'
        }
        self.assertEqual(date_filter, expected_filter)

    def test_sets_start_date_to_end_date_minus_one_if_not_given(self):
        request = MagicMock()
        request.args = MultiDict([('end_date', '2012-08-21')])
        lookup = {}

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)

        date_filter = json.loads(args[0].where).get('versioncreated', {})
        expected_filter = {
            '$gte': '2012-08-20',
            '$lte': '2012-08-21'
        }
        self.assertEqual(date_filter, expected_filter)

    @mock.patch('publicapi.items.service.date', wraps=date)
    def test_sets_end_date_to_today_and_start_day_to_yesterday_if_both_not_given(
        self, fake_date_class
    ):
        request = MagicMock()
        request.args = MultiDict()
        lookup = {}

        fake_date_class.today.return_value = date(2014, 7, 15)

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)

        date_filter = json.loads(args[0].where).get('versioncreated', {})
        expected_filter = {
            '$gte': '2014-07-14',
            '$lte': '2014-07-15'
        }
        self.assertEqual(date_filter, expected_filter)

    @mock.patch('publicapi.items.service.date', wraps=date)
    def test_raises_correct_error_for_start_date_in_future(self, fake_date_class):
        request = MagicMock()
        request.args = MultiDict([('start_date', '2007-10-31')])
        lookup = {}

        fake_date_class.today.return_value = date(2007, 10, 30)

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(
            ex.desc,
            "Start date (2007-10-31) must not be set in the future "
            "(current server date: 2007-10-30)"
        )

    @mock.patch('publicapi.items.service.date', wraps=date)
    def test_raises_correct_error_for_end_date_in_future(self, fake_date_class):
        request = MagicMock()
        request.args = MultiDict([('end_date', '2007-10-31')])
        lookup = {}

        fake_date_class.today.return_value = date(2007, 10, 30)

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(
            ex.desc,
            "End date (2007-10-31) must not be set in the future "
            "(current server date: 2007-10-30)"
        )


class ParseIsoDateMethodTestCase(ItemsServiceTestCase):
    """Tests for the parse_iso_date() helper method."""

    def test_returns_none_if_none_given(self):
        klass = self._get_target_class()
        result = klass.parse_iso_date(None)
        self.assertIsNone(result)

    def test_returns_date_object_on_valid_iso_date_string(self):
        klass = self._get_target_class()
        result = klass.parse_iso_date('2015-05-15')
        self.assertEqual(result, date(2015, 5, 15))

    def test_raises_value_error_on_invalid_iso_date_string(self):
        klass = self._get_target_class()
        with self.assertRaises(ValueError):
            klass.parse_iso_date('5th May 2015')


fake_super_find_one = MagicMock(name='fake super().find_one')


@mock.patch('publicapi.items.service.BaseService.find_one', fake_super_find_one)
class FindOneMethodTestCase(ItemsServiceTestCase):
    """Tests for the find_one() method."""

    def setUp(self):
        super().setUp()
        fake_super_find_one.reset_mock()

    @mock.patch('publicapi.items.service.ItemsService._check_request_params')
    def test_correctly_invokes_parameter_validation(self, fake_check_params):
        fake_request = MagicMock()
        lookup = {'_id': 'my_item'}

        instance = self._make_one()
        instance.find_one(fake_request, **lookup)

        self.assertTrue(fake_check_params.called)
        args, kwargs = fake_check_params.call_args

        self.assertGreater(len(args), 0)
        self.assertEqual(args[0], fake_request)
        self.assertEqual(kwargs.get('allow_filtering'), False)

        whitelist_arg = kwargs.get('whitelist')
        if whitelist_arg is not None:
            # NOTE: the whitelist argument is converted to a list, because any
            # iterable type is valid, not just lists
            self.assertEqual(list(whitelist_arg), [])
        else:
            # whitelist can also be passed as a positional argument
            self.assertGreater(len(args), 1)
            self.assertEqual(list(args[1]), [])

    def test_invokes_superclass_method_with_given_arguments(self):
        request = MagicMock()
        lookup = {'_id': 'my_item'}

        instance = self._make_one()
        instance.find_one(request, **lookup)

        self.assertTrue(fake_super_find_one.called)
        args, kwargs = fake_super_find_one.call_args
        self.assertEqual(len(args), 1)
        self.assertIs(args[0], request)
        self.assertEqual(kwargs, lookup)

    def test_provides_request_object_to_superclass_if_not_given(self):
        lookup = {'_id': 'my_item'}

        instance = self._make_one()
        instance.find_one(None, **lookup)

        self.assertTrue(fake_super_find_one.called)
        args, kwargs = fake_super_find_one.call_args
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], ParsedRequest)
