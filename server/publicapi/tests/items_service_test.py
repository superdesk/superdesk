# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from publicapi.tests import ApiTestCase
from unittest import mock
from unittest.mock import MagicMock


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


fake_super_get = MagicMock(name='fake super().get')


@mock.patch('publicapi.items.service.BaseService.get', fake_super_get)
class GetMethodTestCase(ItemsServiceTestCase):
    """Tests for the get() method."""

    def setUp(self):
        super().setUp()
        fake_super_get.reset_mock()

    def test_invokes_superclass_method_with_given_arguments(self):
        request = MagicMock()
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
        request.args = dict(q='{"language": "de"}')
        lookup = {}

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)
        self.assertEqual(args[0].where, '{"language": "de"}')

    def test_raises_correct_error_on_unexpected_parameters(self):
        request = MagicMock()
        request.args = dict(foo='bar')
        lookup = {}

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(ex.desc, 'Unexpected parameter (foo)')


fake_super_find_one = MagicMock(name='fake super().find_one')


@mock.patch('publicapi.items.service.BaseService.find_one', fake_super_find_one)
class FindOneMethodTestCase(ItemsServiceTestCase):
    """Tests for the find_one() method."""

    def setUp(self):
        super().setUp()
        fake_super_find_one.reset_mock()

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

    def test_raises_correct_error_on_unexpected_parameters(self):
        request = MagicMock()
        request.args = dict(foo='bar')
        lookup = {'_id': 'my_item'}

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance.find_one(request, **lookup)

        ex = context.exception
        self.assertEqual(ex.desc, 'Unexpected parameter (foo)')

    def test_raises_error_with_descriptive_msg_on_filtering_attempt(self):
        request = MagicMock()
        request.args = dict(q='{"language": "en"}')
        lookup = {'_id': 'my_item'}

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance.find_one(request, **lookup)

        ex = context.exception
        self.assertEqual(
            ex.desc,
            'Filtering is not supported when retrieving a single item '
            '(the "q" parameter)'
        )
