# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.tests import TestCase
from unittest import mock


class AutoRegisteredMetaTest(TestCase):
    """Base class for AutoRegisteredMeta metaclass tests."""

    def _get_target_metacls(self):
        """Return the metaclass under test.

        Make the test fail immediately if the metaclass cannot be imported.
        """
        try:
            from superdesk.io.ingest_service import AutoRegisteredMeta
        except ImportError:
            self.fail(
                "Could not import metaclass under test "
                "(AutoRegisteredMeta).")
        else:
            return AutoRegisteredMeta


@mock.patch('superdesk.io.ingest_service.register_provider')
class CreatingNewClassTestCase(AutoRegisteredMetaTest):
    """Tests for the new class creation process."""

    def test_creates_new_class_on_invocation(self, fake_register):
        metacls = self._get_target_metacls()

        BaseCls = type('BaseCls', (), {})
        new_class = metacls('NewClass', (BaseCls,), {'foo': 'bar', 'baz': 42})

        self.assertEqual(new_class.__name__, 'NewClass')
        self.assertTrue(issubclass(new_class, BaseCls))

        self.assertTrue(hasattr(new_class, 'foo'))
        self.assertEqual(new_class.foo, 'bar')
        self.assertTrue(hasattr(new_class, 'baz'))
        self.assertEqual(new_class.baz, 42)

    @mock.patch('superdesk.io.ingest_service.providers', {})
    def test_registers_new_provider_classes(self, fake_register):
        metacls = self._get_target_metacls()

        new_class_errors = [(1234, 'Error 1234')]

        new_class = metacls(
            'NewClass',
            (),
            dict(ERRORS=new_class_errors, PROVIDER='provider_name')
        )

        self.assertTrue(fake_register.called)
        args, _ = fake_register.call_args
        self.assertEqual(len(args), 3)

        self.assertEqual(args[0], 'provider_name')
        self.assertIs(args[1], new_class)
        self.assertEqual(args[2], new_class_errors)

    def test_does_not_register_non_provider_classes(self, fake_register):
        metacls = self._get_target_metacls()
        metacls('NewClass', (), {})  # NOTE: no PROVIDER attribute
        self.assertFalse(fake_register.called)

    @mock.patch(
        'superdesk.io.ingest_service.providers',
        {'provider_x': 'ClassX'}
    )
    def test_raises_error_on_duplicate_provider_name(self, fake_register):
        metacls = self._get_target_metacls()

        try:
            with self.assertRaises(TypeError) as exc_context:
                metacls('NewClass', (), dict(ERRORS=[], PROVIDER='provider_x'))
        except:
            self.fail('Expected exception type was not raised.')

        ex = exc_context.exception
        self.assertEqual(
            str(ex),
            "PROVIDER provider_x already exists (ClassX).")

    def test_raises_error_if_provider_class_lacks_errors_attribute(
        self, fake_register
    ):
        metacls = self._get_target_metacls()
        try:
            with self.assertRaises(AttributeError) as exc_context:
                # NOTE: no ERRORS attribute
                metacls('NewClass', (), {'PROVIDER': 'foo'})
        except:
            self.fail("Expected exception type was not raised.")

        ex = exc_context.exception
        self.assertEqual(
            str(ex),
            "Provider class NewClass must define the ERRORS list attribute.")


class IngestServiceTest(TestCase):
    """Tests for the base IngestService class."""

    def _get_target_class(self):
        """Return the class under test.

        Make the test fail immediately if the class cannot be imported.
        """
        try:
            from superdesk.io.ingest_service import IngestService
        except ImportError:
            self.fail("Could not import class under test (IngestService).")
        else:
            return IngestService

    def test_has_correct_metaclass(self):
        from superdesk.io.ingest_service import AutoRegisteredMeta
        klass = self._get_target_class()
        self.assertIsInstance(klass, AutoRegisteredMeta)
