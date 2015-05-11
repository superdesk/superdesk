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

from settings import MAX_VALUE_OF_PUBLISH_SEQUENCE
from superdesk.celery_app import set_key, update_key


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

    def format(self, article, provider):
        """Formats the article and returns the transformed string"""
        raise NotImplementedError()

    def can_format(self, format_type):
        """Test if formatter can format for given type."""
        raise NotImplementedError()

    def generate_sequence_number(self, output_channel):
        """
        Generates Published Sequence Number for the passed output_channel
        """

        assert (output_channel is not None), "Output Channel can't be null"

        sequence_key_name = "{output_channel_name}_output_channel_seq".format(
            output_channel_name=output_channel.get('name')).lower()

        sequence_number = update_key(sequence_key_name, flag=True)
        max_seq_number = MAX_VALUE_OF_PUBLISH_SEQUENCE

        if output_channel.get('sequence_num_settings'):
            if sequence_number == 0 or sequence_number == 1:
                sequence_number = output_channel['sequence_num_settings']['min']
                set_key(sequence_key_name, value=sequence_number)

            max_seq_number = output_channel['sequence_num_settings']['max']

        if sequence_number == max_seq_number:
            set_key(sequence_key_name)

        return sequence_number


def get_formatter(format_type):
    """Get parser for given xml.

    :param etree: parsed xml
    """
    for formatter in formatters:
        if formatter.can_format(format_type):
            return formatter


import apps.publish.formatters.nitf_formatter  # NOQA
