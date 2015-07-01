# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging


formatters = []
logger = logging.getLogger(__name__)


class FormatterRegistry(type):
    """Registry metaclass for formatters."""

    def __init__(cls, name, bases, attrs):
        """Register sub-classes of Formatter class when defined."""
        super(FormatterRegistry, cls).__init__(name, bases, attrs)
        if name != 'Formatter':
            formatters.append(cls())


class Formatter(metaclass=FormatterRegistry):
    """Base Formatter class for all types of Formatters like News ML 1.2, News ML G2, NITF, etc."""

    def format(self, article, subscriber):
        """Formats the article and returns the transformed string"""
        raise NotImplementedError()

    def can_format(self, format_type, article):
        """Test if formatter can format for given article."""
        raise NotImplementedError()


def get_formatter(format_type, article):
    """Get parser for given xml.

    :param etree: parsed xml
    """
    for formatter in formatters:
        if formatter.can_format(format_type, article):
            return formatter


import apps.publish.formatters.nitf_formatter  # NOQA
import apps.publish.formatters.aap_ipnews_formatter  # NOQA
import apps.publish.formatters.anpa_formatter  # NOQA
import apps.publish.formatters.ninjs_formatter  # NOQA
import apps.publish.formatters.newsml_1_2_formatter  # NOQA
import apps.publish.formatters.newsml_g2_formatter  # NOQA
import apps.publish.formatters.aap_bulletinbuilder_formatter  # NOQA
import apps.publish.formatters.aap_sms_formatter  # NOQA
