# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import arrow
import datetime
from pytz import utc, timezone  # flake8: noqa

tzinfo = getattr(datetime, 'tzinfo', object)


def utcnow():
    """Get tz aware datetime object.

    Remove microseconds which can't be persisted by mongo so we have
    the values consistent in both mongo and elastic.
    """
    if hasattr(datetime.datetime, 'now'):
        now = datetime.datetime.now(tz=utc)
    else:
        now = datetime.datetime.utcnow()
    return now.replace(microsecond=0)


def get_date(date_or_string):
    if date_or_string:
        return arrow.get(date_or_string).datetime


def get_expiry_date(minutes, offset=None):
    if offset:
        if type(offset) is not datetime:
            return offset + datetime.timedelta(minutes=minutes)
        else:
            raise TypeError('offset must be a datetime.date, not a %s' % type(offset))
    else:
        return utcnow() + datetime.timedelta(minutes=minutes)
