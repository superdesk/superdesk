
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
