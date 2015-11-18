# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import unittest
from macros.take_key_validator import validate
from nose.tools import assert_raises


class TakeKeyValidatorTestCase(unittest.TestCase):

    def test_validation_fails(self):
        item = {'body_html': '$100'}
        with assert_raises(KeyError):
            validate(item)

    def test_validation_fails_empty(self):
        item = {'body_html': '$100', 'anpa_take_key': ''}
        with assert_raises(KeyError):
            validate(item)

    def test_validation_fails_white_space(self):
        item = {'body_html': '$100', 'anpa_take_key': '  '}
        with assert_raises(KeyError):
            validate(item)

    def test_validation_succeeds(self):
        item = {'body_html': '$100', 'anpa_take_key': 'Update'}
        res = validate(item)
        self.assertIsNotNone(res)
