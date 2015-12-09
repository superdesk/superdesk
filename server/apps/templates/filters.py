# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk.utc import get_date, timezone
from superdesk import config

logger = logging.getLogger(__name__)


def format_datetime_filter(date_or_string, timezone_string=None, date_format=None):
    """
    Convert date or string to another timezone
    :param str date_or_string:
    :param str timezone_string:
    :param str date_format:
    :return str: returns string representation of the date format
    """
    try:
        date_time = get_date(date_or_string)

        timezone_string = timezone_string if timezone_string else config.DEFAULT_TIMEZONE
        tz = timezone(timezone_string)
        if tz:
            date_time = date_time.astimezone(tz)

        if date_format:
            return date_time.strftime(date_format)
        else:
            return str(date_time)

    except:
        logger.warning('Failed to convert datetime. Arguments: Date - {} Timezone - {} format - {}.'.format(
            date_or_string, timezone_string, date_format
        ))
        return ''
