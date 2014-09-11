
import arrow
import datetime
from pytz import utc, timezone # flake8: noqa

tzinfo = getattr(datetime, 'tzinfo', object)


def utcnow():
    """Get tz aware datetime object"""

    if hasattr(datetime.datetime, 'now'):
        return datetime.datetime.now(tz=utc)
    else:
        return datetime.datetime.utcnow()


def get_date(date_or_string):
    if date_or_string:
        return arrow.get(date_or_string).datetime
