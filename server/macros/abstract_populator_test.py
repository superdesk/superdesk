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
from macros.abstract_populator import populate


class AbstractPopulatorTestCase(unittest.TestCase):

    def setUp(self):
        self.body = ("Fountain of Time, or simply Time, is a sculpture by Lorado Taft, "
                     "measuring 126 feet 10 inches (38.66 m) in length, situated at the "
                     "western edge of the Midway Plaisance within Washington Park in "
                     "Chicago, Illinois, in the United States. This location is in the "
                     "Washington Park community area on Chicago's South Side. Inspired "
                     "by Henry Austin Dobson's poem, \"Paradox of Time\", and with its "
                     "100 figures passing before Father Time, the work was created as a "
                     "monument to the first 100 years of peace between the United States "
                     "and Great Britain, resulting from the Treaty of Ghent in 1814. "
                     "Although the fountain's water began running in 1920, the sculpture "
                     "was not dedicated to the city until 1922. The sculpture is a "
                     "contributing structure to the Washington Park United States "
                     "Registered Historic District, which is a National Register of "
                     "Historic Places listing.")

    def test_populate(self):
        item = {'body_html': self.body}
        item = populate(item)
        self.assertEqual(item['abstract'], 'Fountain of Time, or simply Time, is a sculpture by Lorado Taft,')

    def test_populate_without_body(self):
        item = {}
        item = populate(item)
        self.assertEqual(item['abstract'], 'No body found to use for abstract...')
