
import string
import random
from importlib import import_module


def get_random_string(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for i in range(length)])


def import_by_path(path):
    module_path, class_name = path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name)


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
