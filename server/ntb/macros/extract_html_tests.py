# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from .extract_html import extract_html_macro
import unittest


class ExtractHtmlTestCase(unittest.TestCase):

    def test_extract_html_macro(self):
        item = {'body_html': 'test <a href="www.sourcefabric.org">Sourcefabric</a> <br> <span>test <span/>'}
        extract_html_macro(item)
        self.assertEqual(item.get('body_html'),
                         '<p>test <a href="www.sourcefabric.org">Sourcefabric</a> <br> test </p>')
