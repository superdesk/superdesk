# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


class FieldMapper():
    """Base mapper class can be used in all formatters"""

    def map(self, article, category, **kwargs):
        """Formats the article and returns the transformed string"""
        raise NotImplementedError()
