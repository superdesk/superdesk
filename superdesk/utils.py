
import string
import random
from datetime import datetime

DATE_FORMATS = (
    '%Y-%m-%dT%H:%M:%S.%f%z',
    '%Y-%m-%dT%H:%M:%S%z',
    '%Y-%m-%dT%H:%M:%S',
)

def get_random_string(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for i in range(length)])

def str_to_date(date_str):
    """Parse datetime string."""
    for format in DATE_FORMATS:
        try:
            return datetime.strptime(date_str.replace('+00:', '+00'), format)
        except ValueError:
            pass
    return date_str
