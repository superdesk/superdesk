# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


def json_get_value(json, path):
    '''
    Get the value from specified json path
    json: json document
    path: a list of keys
    '''
    crt = json
    for name in path:
        if name in crt:
            crt = crt[name]
        else:
            return None
    return crt


def json_set_value(json, path, value):
    '''
    Set the value at the specified json path.
    Create the path if it don't exists.
    json: json document
    path: a list of keys
    value: value to be set
    '''
    crt = json
    for name in path[:-1]:
        if name not in crt:
            crt[name] = {}
        crt = crt[name]
    crt[path[-1]] = value


def json_merge_values(destination, source, path, merge_values_mode):
    '''
    On destination json merge the source value defined by path.
    The values are merged by calling the merge_values_mode method
    destination: destination json
    source: source json
    path: list of keys
    merge_values_mode: a method that will get the values as parameters
    and will return the merged value
    '''
    destination_term = json_get_value(destination, path)
    source_term = json_get_value(source, path)

    if not source_term:
        return

    if destination_term:
        json_set_value(destination, path, merge_values_mode(destination_term, source_term))
    else:
        json_set_value(destination, path, source_term)


def json_copy_values(destination, source, keys):
    '''
    If a key is not present on destination it will be copied from source (if exists)
    destination - destination json
    source - source json
    keys - list of keys
    '''
    for key in keys:
        if key not in destination and key in source:
            destination[key] = source[key]
