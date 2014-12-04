import os
import string
import random
import bcrypt
from enum import Enum
from importlib import import_module
from flask import current_app as app
from .utc import utcnow


class FileSortAttributes(Enum):
    """
    Enum defining the File Story Attributes.
    """
    name = 1
    created = 2
    modified = 3


class SortOrder(Enum):
    """
    Enum defining the sort order.
    """
    asc = 1
    desc = 2


def last_updated(*docs):
    """Get last last updated date for all given docs."""
    dates = [d.get(app.config['LAST_UPDATED']) for d in docs if d and d.get(app.config['LAST_UPDATED'])]
    return max(dates) if dates else utcnow()


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


def get_sorted_files(path, sort_by=FileSortAttributes.name, sort_order=SortOrder.asc):
    """
    Get the list of files based on the sort order.
    Sort is allowed on name, created and modified datetime
    :param path: directory path
    :param sort_by: "name", "created", "modified"
    :param sort_order: "asc" - ascending, "desc" - descending
    :return: list of files from the path
    """
    # get the files
    files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
    if sort_by == FileSortAttributes.name:
        files.sort(reverse=(sort_order == SortOrder.desc))
    elif sort_by == FileSortAttributes.created:
        files.sort(key=lambda file: os.path.getctime(os.path.join(path, file)), reverse=(sort_order == SortOrder.desc))
    elif sort_by == FileSortAttributes.modified:
        files.sort(key=lambda file: os.path.getmtime(os.path.join(path, file)), reverse=(sort_order == SortOrder.desc))
    else:
        files.sort(reverse=(sort_order == SortOrder.desc))

    return files


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
