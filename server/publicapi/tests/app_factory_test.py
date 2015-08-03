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


@mock.patch('publicapi.importlib', MagicMock())
@mock.patch('publicapi.MongoJSONEncoder', MagicMock())
@mock.patch('publicapi.SuperdeskDataLayer', MagicMock())
@mock.patch('publicapi.settings')
class ApiApplicationFactoryTestCase(ApiTestCase):
    """Base class for the API application factory tests."""

    def _init_settings(self, settings):
        """Initialize given settings to a bare usable minimum.

        :param dict settings: default settings of the public API application
        """
        settings.DOMAIN = {}
        settings.INSTALLED_APPS = []

    def setUp(self):
        try:
            from publicapi import get_app
        except ImportError:
            # failed import should result in a failed test, not in an error
            # because the test did not run
            self.fail("Could not import API application factory.")
        else:
            self.app_factory = get_app

    def test_returned_application_object_type(self, fake_settings):
        from eve import Eve
        self._init_settings(fake_settings)

        app = self.app_factory()

        self.assertIsInstance(app, Eve)

    def test_created_app_uses_default_settings(self, fake_settings):
        fake_settings.DOMAIN = {'domain_one': {}, 'domain_two': {}}
        fake_settings.INSTALLED_APPS = ['package.one', 'package.two']

        app = self.app_factory()

        self.assertEqual(
            sorted(app.settings.get('DOMAIN', {}).keys()),
            ['domain_one', 'domain_two']
        )
        self.assertEqual(
            app.settings.get('INSTALLED_APPS'),
            ['package.one', 'package.two']
        )

    def test_created_app_uses_provided_config_settings(self, fake_settings):
        self._init_settings(fake_settings)

        config = {'FOO': 'BAR'}
        app = self.app_factory(config)

        self.assertEqual(app.settings.get('FOO'), 'BAR')

    def test_provided_config_takes_precedence_over_default_settings(
        self, fake_settings
    ):
        self._init_settings(fake_settings)
        fake_settings.FOO = 'BAR'

        config = {'FOO': 'BAR_BAZ'}
        app = self.app_factory(config)

        self.assertEqual(app.settings.get('FOO'), 'BAR_BAZ')

    def test_created_app_ignores_non_uppercase_default_settings(
        self, fake_settings
    ):
        self._init_settings(fake_settings)
        fake_settings.foo = 'value 1'
        fake_settings.Bar = 'value 2'

        app = self.app_factory()

        self.assertNotIn('foo', app.settings)
        self.assertNotIn('Bar', app.settings)

        # does also not, for example, capitalize non-uppercase settings
        self.assertNotIn('FOO', app.settings)
        self.assertNotIn('BAR', app.settings)

    def test_initializes_all_installed_applications(self, fake_settings):
        self._init_settings(fake_settings)

        fake_settings.INSTALLED_APPS = ['package.one', 'package.two']

        # mock importlib package...
        module_one = MagicMock(name='package.one')
        module_two = MagicMock(name='package.two')
        modules = {'package.one': module_one, 'package.two': module_two}

        def module_from_name(module_name):
            return modules.get(module_name, MagicMock(name='unknown.module'))

        fake_importlib = MagicMock(name='fake_importlib')
        fake_importlib.import_module.side_effect = module_from_name
        # ...done mocking

        with mock.patch('publicapi.importlib', fake_importlib):
            app = self.app_factory()

        for module in (module_one, module_two):
            self.assertTrue(module.init_app.called)
            args, kwargs = module.init_app.call_args
            self.assertGreater(len(args), 0)
            self.assertIs(args[0], app)

    def test_no_error_if_installed_app_does_not_have_init_app_method(
        self, fake_settings
    ):
        self._init_settings(fake_settings)

        fake_settings.INSTALLED_APPS = ['some.app']

        # mock importlib package...
        some_app = MagicMock(name='some.app')
        some_app.init_app.side_effect = AttributeError

        fake_importlib = MagicMock(name='fake_importlib')
        fake_importlib.import_module.return_value = some_app
        # ...done mocking

        with mock.patch('publicapi.importlib', fake_importlib):
            try:
                self.app_factory()
            except Exception as ex:
                self.fail(
                    "An error unexpectedly raised ({}).".format(repr(ex)[:-2])
                )

    def test_registers_all_domain_resources(self, fake_settings):
        self._init_settings(fake_settings)

        endpoint_1_config = MagicMock(name='endpoint_1_config')
        endpoint_2_config = MagicMock(name='endpoint_2_config')

        config = {
            'DOMAIN': {
                'endpoint_1': endpoint_1_config,
                'endpoint_2': endpoint_2_config
            }
        }

        with mock.patch('publicapi.Eve'):
            app = self.app_factory(config)

        expected_calls = [
            mock.call('endpoint_1', endpoint_1_config),
            mock.call('endpoint_2', endpoint_2_config),
        ]
        app.register_resource.assert_has_calls(expected_calls, any_order=True)

    def test_media_storage_is_properly_initialized(self, fake_settings):
        from superdesk.storage.desk_media_storage import SuperdeskGridFSMediaStorage
        self._init_settings(fake_settings)
        fake_settings.AMAZON_CONTAINER_NAME = ''

        app = self.app_factory()

        self.assertIsInstance(app.media, SuperdeskGridFSMediaStorage)

    def test_amazon_media_storage_is_properly_initialized(self, fake_settings):
        from superdesk.storage.amazon.amazon_media_storage import AmazonMediaStorage
        self._init_settings(fake_settings)
        fake_settings.AMAZON_CONTAINER_NAME = 'Test'
        fake_settings.AMAZON_ACCESS_KEY_ID = 'test'
        fake_settings.AMAZON_SECRET_ACCESS_KEY = 'test'

        app = self.app_factory()

        self.assertIsInstance(app.media, AmazonMediaStorage)
