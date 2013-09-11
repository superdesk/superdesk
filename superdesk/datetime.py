import datetime

class UTC(datetime.tzinfo):
    """UTC tz"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

def utcnow():
    """Get tz aware datetime object"""
    return datetime.datetime.now(tz=UTC())
