# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
import bcrypt
from uuid import uuid4
from datetime import datetime
from bson import ObjectId
from enum import Enum
from importlib import import_module
from eve.utils import config


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


def get_random_string(length=12):
    return str(uuid4())


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


def merge_dicts(dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


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


def json_serialize_datetime_objectId(obj):
    """
    serialize so that objectid and date are converted to appropriate format.
    """
    if isinstance(obj, datetime):
        return str(datetime.strftime(obj, config.DATE_FORMAT))

    if isinstance(obj, ObjectId):
        return str(obj)
