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
from flask import Flask
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


class CheckForUnknownParamsMethodTestCase(ItemsServiceTestCase):
    """Tests for the _check_for_unknown_params() helper method."""

    def test_does_not_raise_an_error_on_valid_parameters(self):
        request = MagicMock()
        request.args = MultiDict([('sort_by', 'language')])
        instance = self._make_one()

        try:
            instance._check_for_unknown_params(request, ('foo', 'sort_by', 'bar'))
        except Exception as ex:
            self.fail("Exception unexpectedly raised ({})".format(ex))

    def test_raises_correct_error_on_unexpected_parameters(self):
        request = MagicMock()
        request.args = MultiDict([('param_x', 'something')])

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance._check_for_unknown_params(request, ('foo', 'bar'))

        ex = context.exception
        self.assertEqual(ex.payload, 'Unexpected parameter (param_x)')

    def test_raises_descriptive_error_on_filtering_disabled(self):
        request = MagicMock()
        request.args = MultiDict([('q', '{"language": "en"}')])

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance._check_for_unknown_params(
                request, whitelist=(), allow_filtering=False)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            'Filtering is not supported when retrieving a single object '
            '(the "q" parameter)'
        )

    def test_raises_descriptive_error_on_disabled_start_date_filtering(self):
        request = MagicMock()
        request.args = MultiDict([('start_date', '2015-01-01')])

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance._check_for_unknown_params(
                request, whitelist=(), allow_filtering=False)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            'Filtering by date range is not supported when retrieving a '
            'single object (the "start_date" parameter)'
        )

    def test_raises_descriptive_error_on_disabled_end_date_filtering(self):
        request = MagicMock()
        request.args = MultiDict([('end_date', '2015-01-01')])

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance._check_for_unknown_params(
                request, whitelist=(), allow_filtering=False)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            'Filtering by date range is not supported when retrieving a '
            'single object (the "end_date" parameter)'
        )

    def test_raises_correct_error_on_duplicate_parameters(self):
        request = MagicMock()
        request.args = MultiDict([('foo', 'value 1'), ('foo', 'value 2')])

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance._check_for_unknown_params(request, whitelist=('foo',))

        ex = context.exception
        self.assertEqual(
            ex.payload, "Multiple values received for parameter (foo)")


fake_super_get = MagicMock(name='fake super().get')


@mock.patch('publicapi.items.service.BaseService.get', fake_super_get)
class GetMethodTestCase(ItemsServiceTestCase):
    """Tests for the get() method."""

    def setUp(self):
        super().setUp()
        fake_super_get.reset_mock()

    @mock.patch('publicapi.items.service.ItemsService._check_for_unknown_params')
    def test_correctly_invokes_parameter_validation(self, fake_check_unknown):
        fake_request = MagicMock()
        fake_request.args = MultiDict()
        lookup = {}

        instance = self._make_one()
        instance.get(fake_request, lookup)

        self.assertTrue(fake_check_unknown.called)
        args, kwargs = fake_check_unknown.call_args

        self.assertGreater(len(args), 0)
        self.assertEqual(args[0], fake_request)

        expected_whitelist = sorted([
            'start_date', 'end_date',
            'exclude_fields', 'include_fields',
            'q'
        ])

        whitelist_arg = kwargs.get('whitelist')
        if whitelist_arg is not None:
            # NOTE: the whitelist argument is converted to a list, because any
            # iterable type is valid, not just lists
            self.assertEqual(sorted(list(whitelist_arg)), expected_whitelist)
        else:
            # whitelist can also be passed as a positional argument
            self.assertGreater(len(args), 1)
            self.assertEqual(sorted(list(args[1])), expected_whitelist)

    @mock.patch('publicapi.items.service.ItemsService._set_fields_filter')
    def test_sets_fields_filter_on_request_object(self, fake_set_fields_filter):
        fake_request = MagicMock()
        fake_request.args = MultiDict()
        fake_request.projection = None
        lookup = {}

        instance = self._make_one()
        instance.get(fake_request, lookup)

        self.assertTrue(fake_set_fields_filter.called)
        args, kwargs = fake_set_fields_filter.call_args

        self.assertGreater(len(args), 0)
        self.assertIs(args[0], fake_request)

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

    def test_raises_correct_error_on_invalid_start_date_parameter(self):
        request = MagicMock()
        request.args = MultiDict([('start_date', '2015-13-35')])
        lookup = {}

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            ("start_date parameter must be a valid ISO 8601 date (YYYY-MM-DD) "
             "without the time part"))

    def test_raises_correct_error_on_invalid_end_date_parameter(self):
        request = MagicMock()
        request.args = MultiDict([('end_date', '2015-13-35')])
        lookup = {}

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            ("end_date parameter must be a valid ISO 8601 date (YYYY-MM-DD) "
             "without the time part"))

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
            ex.payload, "Start date must not be greater than end date")

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
            '$gte': '2012-08-21T00:00:00+0000',
            '$lt': '2012-08-27T00:00:00+0000'  # end_date + 1 day
        }
        self.assertEqual(date_filter, expected_filter)

    @mock.patch('publicapi.items.service.utcnow')
    def test_sets_end_date_to_today_if_not_given(self, fake_utcnow):
        request = MagicMock()
        request.args = MultiDict([('start_date', '2012-08-21')])
        lookup = {}

        fake_utcnow.return_value.date.return_value = date(2014, 7, 15)

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)

        date_filter = json.loads(args[0].where).get('versioncreated', {})
        expected_filter = {
            '$gte': '2012-08-21T00:00:00+0000',
            '$lt': '2014-07-16T00:00:00+0000'  # today + 1 day
        }
        self.assertEqual(date_filter, expected_filter)

    def test_sets_start_date_equal_to_end_date_if_not_given(self):
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
            '$gte': '2012-08-21T00:00:00+0000',
            '$lt': '2012-08-22T00:00:00+0000'  # end_date + 1 day
        }
        self.assertEqual(date_filter, expected_filter)

    @mock.patch('publicapi.items.service.utcnow')
    def test_sets_end_date_and_start_date_to_today_if_both_not_given(
        self, fake_utcnow
    ):
        request = MagicMock()
        request.args = MultiDict()
        lookup = {}

        fake_utcnow.return_value.date.return_value = date(2014, 7, 15)

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)

        date_filter = json.loads(args[0].where).get('versioncreated', {})
        expected_filter = {
            '$gte': '2014-07-15T00:00:00+0000',
            '$lt': '2014-07-16T00:00:00+0000'  # today + 1 day
        }
        self.assertEqual(date_filter, expected_filter)

    def test_creates_correct_query_if_start_and_end_date_are_the_same(self):
        request = MagicMock()
        request.args = MultiDict([
            ('start_date', '2010-09-17'),
            ('end_date', '2010-09-17')]
        )
        lookup = {}

        instance = self._make_one()
        instance.get(request, lookup)

        self.assertTrue(fake_super_get.called)
        args, kwargs = fake_super_get.call_args
        self.assertGreater(len(args), 0)

        date_filter = json.loads(args[0].where).get('versioncreated', {})
        expected_filter = {
            '$gte': '2010-09-17T00:00:00+0000',
            '$lt': '2010-09-18T00:00:00+0000'
        }
        self.assertEqual(date_filter, expected_filter)

    @mock.patch('publicapi.items.service.utcnow')
    def test_raises_correct_error_for_start_date_in_future(self, fake_utcnow):
        request = MagicMock()
        request.args = MultiDict([('start_date', '2007-10-31')])
        lookup = {}

        fake_utcnow.return_value.date.return_value = date(2007, 10, 30)

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            "Start date (2007-10-31) must not be set in the future "
            "(current server date (UTC): 2007-10-30)"
        )

    @mock.patch('publicapi.items.service.utcnow')
    def test_raises_correct_error_for_end_date_in_future(self, fake_utcnow):
        request = MagicMock()
        request.args = MultiDict([('end_date', '2007-10-31')])
        lookup = {}

        fake_utcnow.return_value.date.return_value = date(2007, 10, 30)

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance.get(request, lookup)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            "End date (2007-10-31) must not be set in the future "
            "(current server date (UTC): 2007-10-30)"
        )


class ParseIsoDateMethodTestCase(ItemsServiceTestCase):
    """Tests for the _parse_iso_date() helper method."""

    def test_returns_none_if_none_given(self):
        klass = self._get_target_class()
        result = klass._parse_iso_date(None)
        self.assertIsNone(result)

    def test_returns_date_object_on_valid_iso_date_string(self):
        klass = self._get_target_class()
        result = klass._parse_iso_date('2015-05-15')
        self.assertEqual(result, date(2015, 5, 15))

    def test_raises_value_error_on_invalid_iso_date_string(self):
        klass = self._get_target_class()
        with self.assertRaises(ValueError):
            klass._parse_iso_date('5th May 2015')


class SetFieldsFilterMethodTestCase(ItemsServiceTestCase):
    """Tests for the _set_fields_filter() helper method."""

    def test_raises_error_if_requesting_to_exclude_required_field(self):
        request = MagicMock()
        request.args = MultiDict([('exclude_fields', 'uri')])
        request.projection = None

        from publicapi.errors import BadParameterValueError
        instance = self._make_one()

        with self.assertRaises(BadParameterValueError) as context:
            instance._set_fields_filter(request)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            'Cannot exclude a content field required by the NINJS format '
            '(uri).'
        )

    def test_raises_error_if_field_whitelist_and_blacklist_both_given(self):
        request = MagicMock()
        request.args = MultiDict([
            ('include_fields', 'language'),
            ('exclude_fields', 'body_text'),
        ])
        request.projection = None

        from publicapi.errors import UnexpectedParameterError
        instance = self._make_one()

        with self.assertRaises(UnexpectedParameterError) as context:
            instance._set_fields_filter(request)

        ex = context.exception
        self.assertEqual(
            ex.payload,
            'Cannot both include and exclude content fields at the same time.'
        )

    def test_raises_error_if_whitelisting_unknown_content_field(self):
        request = MagicMock()
        request.args = MultiDict([('include_fields', 'field_x')])
        request.projection = None

        from publicapi.errors import BadParameterValueError
        from publicapi.items import ItemsResource

        instance = self._make_one()

        fake_schema = {'foo': 'schema_bar'}
        with mock.patch.object(ItemsResource, 'schema', new=fake_schema):
            with self.assertRaises(BadParameterValueError) as context:
                instance._set_fields_filter(request)

            ex = context.exception
            self.assertEqual(
                ex.payload, 'Unknown content field to include (field_x).')

    def test_raises_error_if_blacklisting_unknown_content_field(self):
        request = MagicMock()
        request.args = MultiDict([('exclude_fields', 'field_x')])
        request.projection = None

        from publicapi.errors import BadParameterValueError
        from publicapi.items import ItemsResource

        instance = self._make_one()

        fake_schema = {'foo': 'schema_bar'}
        with mock.patch.object(ItemsResource, 'schema', new=fake_schema):
            with self.assertRaises(BadParameterValueError) as context:
                instance._set_fields_filter(request)

            ex = context.exception
            self.assertEqual(
                ex.payload, 'Unknown content field to exclude (field_x).')

    def test_filters_out_blacklisted_fields_if_requested(self):
        request = MagicMock()
        request.args = MultiDict([('exclude_fields', 'language,version')])
        request.projection = None

        instance = self._make_one()
        instance._set_fields_filter(request)

        projection = json.loads(request.projection) if request.projection else {}
        expected_projection = {
            'language': 0,
            'version': 0,
        }
        self.assertEqual(projection, expected_projection)

    def test_filters_out_all_but_whitelisted_fields_if_requested(self):
        request = MagicMock()
        request.args = MultiDict([('include_fields', 'body_text,byline')])
        request.projection = None

        instance = self._make_one()
        instance._set_fields_filter(request)

        projection = json.loads(request.projection) if request.projection else {}
        expected_projection = {
            'body_text': 1,
            'byline': 1,
        }
        self.assertEqual(projection, expected_projection)


fake_super_find_one = MagicMock(name='fake super().find_one')


@mock.patch('publicapi.items.service.BaseService.find_one', fake_super_find_one)
class FindOneMethodTestCase(ItemsServiceTestCase):
    """Tests for the find_one() method."""

    def setUp(self):
        super().setUp()
        fake_super_find_one.reset_mock()

    @mock.patch('publicapi.items.service.ItemsService._check_for_unknown_params')
    def test_correctly_invokes_parameter_validation(self, fake_check_unknown):
        fake_request = MagicMock()
        fake_request.args = MultiDict()
        lookup = {'_id': 'my_item'}

        instance = self._make_one()
        instance.find_one(fake_request, **lookup)

        self.assertTrue(fake_check_unknown.called)
        args, kwargs = fake_check_unknown.call_args

        self.assertGreater(len(args), 0)
        self.assertEqual(args[0], fake_request)
        self.assertEqual(kwargs.get('allow_filtering'), False)

        expected_whitelist = sorted(['exclude_fields', 'include_fields'])

        whitelist_arg = kwargs.get('whitelist')
        if whitelist_arg is not None:
            # NOTE: the whitelist argument is converted to a list, because any
            # iterable type is valid, not just lists
            self.assertEqual(sorted(list(whitelist_arg)), expected_whitelist)
        else:
            # whitelist can also be passed as a positional argument
            self.assertGreater(len(args), 1)
            self.assertEqual(sorted(list(args[1])), expected_whitelist)

    @mock.patch('publicapi.items.service.ItemsService._set_fields_filter')
    def test_sets_fields_filter_on_request_object(self, fake_set_fields_filter):
        fake_request = MagicMock()
        fake_request.args = MultiDict()
        fake_request.projection = None
        lookup = {}

        instance = self._make_one()
        instance.find_one(fake_request, **lookup)

        self.assertTrue(fake_set_fields_filter.called)
        args, kwargs = fake_set_fields_filter.call_args

        self.assertGreater(len(args), 0)
        self.assertIs(args[0], fake_request)

    def test_invokes_superclass_method_with_given_arguments(self):
        request = MagicMock()
        request.args = MultiDict()
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


class OnFetchedItemMethodTestCase(ItemsServiceTestCase):
    """Tests for the on_fetched_item() method."""

    def setUp(self):
        super().setUp()

        self.app = Flask(__name__)
        self.app.config['PUBLICAPI_URL'] = 'http://api.com'
        self.app.config['URLS'] = {'items': 'items_endpoint'}

        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()
        super().tearDown()

    def test_sets_uri_field_on_fetched_document(self):
        document = {
            '_id': 'item:123',
            'headline': 'a test item'
        }

        instance = self._make_one(datasource='items')
        instance.on_fetched_item(document)

        self.assertEqual(
            document.get('uri'),
            'http://api.com/items_endpoint/item%3A123'  # %3A == urlquote(':')
        )

    def test_removes_non_ninjs_content_fields_from_fetched_document(self):
        document = {
            '_id': 'item:123',
            '_etag': '12345abcde',
            '_created': '12345abcde',
            '_updated': '12345abcde',
            'headline': 'breaking news'
        }

        instance = self._make_one(datasource='items')
        instance.on_fetched_item(document)

        for field in ('_created', '_etag', '_id', '_updated'):
            self.assertNotIn(field, document)

    def test_does_not_remove_hateoas_links_from_fetched_document(self):
        document = {
            '_id': 'item:123',
            'headline': 'breaking news',
            '_links': {
                'self': {
                    'href': 'link/to/item/itself',
                    'title': 'Item'
                }
            }
        }

        instance = self._make_one(datasource='items')
        instance.on_fetched_item(document)

        expected_links = {
            'self': {'href': 'link/to/item/itself', 'title': 'Item'}
        }
        self.assertEqual(document.get('_links'), expected_links)


class OnFetchedMethodTestCase(ItemsServiceTestCase):
    """Tests for the on_fetched() method."""

    def setUp(self):
        super().setUp()

        self.app = Flask(__name__)
        self.app.config['PUBLICAPI_URL'] = 'http://api.com'
        self.app.config['URLS'] = {'items': 'items_endpoint'}

        self.app_context = self.app.app_context()
        self.app_context.push()
        self.req_context = self.app.test_request_context('items/')
        self.req_context.push()

    def tearDown(self):
        self.req_context.pop()
        self.app_context.pop()
        super().tearDown()

    def test_sets_uri_field_on_all_fetched_documents(self):
        result = {
            '_items': [
                {'_id': 'item:123', 'headline': 'a test item'},
                {'_id': 'item:555', 'headline': 'another item'},
            ]
        }

        instance = self._make_one(datasource='items')
        instance.on_fetched(result)

        documents = result['_items']
        self.assertEqual(
            documents[0].get('uri'),
            'http://api.com/items_endpoint/item%3A123'  # %3A == urlquote(':')
        )
        self.assertEqual(
            documents[1].get('uri'),
            'http://api.com/items_endpoint/item%3A555'  # %3A == urlquote(':')
        )

    def test_removes_non_ninjs_content_fields_from_all_fetched_documents(self):
        result = {
            '_items': [{
                '_id': 'item:123',
                '_etag': '12345abcde',
                '_created': '12345abcde',
                '_updated': '12345abcde',
                'headline': 'breaking news',
            }, {
                '_id': 'item:555',
                '_etag': '67890fedcb',
                '_created': '2121abab',
                '_updated': '2121abab',
                'headline': 'good news',
            }]
        }

        instance = self._make_one(datasource='items')
        instance.on_fetched(result)

        documents = result['_items']
        for doc in documents:
            for field in ('_created', '_etag', '_id', '_updated'):
                self.assertNotIn(field, doc)

    def test_does_not_remove_hateoas_links_from_fetched_documents(self):
        result = {
            '_items': [{
                '_id': 'item:123',
                '_etag': '12345abcde',
                '_created': '12345abcde',
                '_updated': '12345abcde',
                'headline': 'breaking news',
                '_links': {
                    'self': {
                        'href': 'link/to/item_123',
                        'title': 'Item'
                    }
                }
            }, {
                '_id': 'item:555',
                '_etag': '67890fedcb',
                '_created': '2121abab',
                '_updated': '2121abab',
                'headline': 'good news',
                '_links': {
                    'self': {
                        'href': 'link/to/item_555',
                        'title': 'Item'
                    }
                }
            }]
        }

        instance = self._make_one(datasource='items')
        instance.on_fetched(result)

        documents = result['_items']

        expected_links = {
            'self': {'href': 'link/to/item_123', 'title': 'Item'}
        }
        self.assertEqual(documents[0].get('_links'), expected_links)

        expected_links = {
            'self': {'href': 'link/to/item_555', 'title': 'Item'}
        }
        self.assertEqual(documents[1].get('_links'), expected_links)

    def test_sets_collection_self_link_to_relative_original_url(self):
        result = {
            '_items': [],
            '_links': {
                'self': {'href': 'foo/bar/baz'}
            }
        }

        request_url = 'items?start_date=1975-12-31#foo'
        with self.app.test_request_context(request_url):
            instance = self._make_one(datasource='items')
            instance.on_fetched(result)

        self_link = result.get('_links', {}).get('self', {}).get('href')
        self.assertEqual(self_link, 'items?start_date=1975-12-31')


class GetUriMethodTestCase(ItemsServiceTestCase):
    """Tests for the _get_uri() helper method."""

    def setUp(self):
        super().setUp()

        self.app = Flask(__name__)
        self.app.config['PUBLICAPI_URL'] = 'http://api.com'
        self.app.config['URLS'] = {
            'items': 'items_endpoint',
            'packages': 'packages_endpoint'
        }

        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()
        super().tearDown()

    def test_generates_correct_uri_for_non_composite_items(self):
        document = {
            '_id': 'foo:bar',
            'type': 'picture'
        }

        instance = self._make_one(datasource='items')
        result = instance._get_uri(document)

        self.assertEqual(result, 'http://api.com/items_endpoint/foo%3Abar')

    def test_generates_correct_uri_for_composite_items(self):
        document = {
            '_id': 'foo:bar',
            'type': 'composite'
        }

        instance = self._make_one(datasource='items')
        result = instance._get_uri(document)

        self.assertEqual(result, 'http://api.com/packages_endpoint/foo%3Abar')
