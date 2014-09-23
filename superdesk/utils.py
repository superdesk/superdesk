
import string
import random
import bcrypt
from importlib import import_module


def get_random_string(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for i in range(length)])


def import_by_path(path):
    module_path, class_name = path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name)


def get_hash(input_str, salt):
    hashed = bcrypt.hashpw(input_str.encode('UTF-8'), bcrypt.gensalt(salt))
    return hashed.decode('UTF-8')


def is_hashed(input_str):
    """Check if given input_str is hashed."""
    return input_str.startswith('$2a$')


class ListCursor(object):
    """Wrapper for a python list as a cursor."""

    def __init__(self, docs=None):
        self.docs = docs if docs else []

    def __getitem__(self, key):
        return self.docs[key]

    def first(self):
        """Get first doc."""
        return self.docs[0] if self.docs else None

    def count(self, **kwargs):
        """Get total count."""
        return len(self.docs)

    def extra(self, response):
        pass
