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
        self.assertIsNotNone(args[0])

    def test_sets_query_filter_on_request_object_if_present(self):
        request = MagicMock()
        request.args = MultiDict([('q', '{"language": "de"}')])
        lookup = {}

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)
        self.assertEqual(args[0].where, '{"language": "de"}')

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
        expected_filter = {'$gte': '2012-08-21', '$lte': '2012-08-26'}
        self.assertEqual(date_filter, expected_filter)


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
