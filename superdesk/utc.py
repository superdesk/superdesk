
import datetime

tzinfo = getattr(datetime, 'tzinfo', object)

class UTC(tzinfo):
    """UTC tz"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

def utcnow():
    """Get tz aware datetime object"""

    if hasattr(datetime.datetime, 'now'):
        return datetime.datetime.now(tz=UTC())
    else:
        return datetime.datetime.utcnow()
