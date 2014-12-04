
import arrow
import datetime
from pytz import utc, timezone # flake8: noqa

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


def get_expiry_date(minutes):
    return utcnow() + datetime.timedelta(minutes=minutes)
