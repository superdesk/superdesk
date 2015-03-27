# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.resource import Resource


base_dictionary_schema = {
    'name': {
        'type': 'string',
        'unique': True,
        'required': True
    },
    'language_id': {
        'type': 'string',
        'required': True
    },
    'language_name': {
        'type': 'string',
        'required': True
    }
}


class DictionariesResource(Resource):
    '''
    Dictionaries schema
    '''
    schema = base_dictionary_schema
    schema.update({'content': {'type': 'list'}})
    datasource = {
        'source': 'dictionaries',
        'projection': {
            'name': 1,
            'language_id': 1,
            'language_name': 1,
            '_created': 1,
            '_updated': 1,
            '_etag': 1
        }
    }
    item_methods = ['GET', 'PATCH', 'DELETE']
    resource_methods = ['GET', 'POST', 'DELETE']
    privileges = {'POST': 'dictionaries', 'PATCH': 'dictionaries', 'DELETE': 'dictionaries'}


class DictionaryUploadResource(Resource):
    schema = base_dictionary_schema
    schema.update({'dictionary_file': {'type': 'file', 'required': True}})
    datasource = {
        'source': 'dictionaries',
        'projection': {
            'name': 1,
            'language_id': 1,
            'language_name': 1,
            '_created': 1,
            '_updated': 1,
            '_etag': 1
        }
    }
    item_methods = ['PATCH', 'GET', 'DELETE']
    resource_methods = ['POST']
    privileges = {'POST': 'dictionaries', 'PATCH': 'dictionaries'}
