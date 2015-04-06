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
        'required': True
    },
    'language_id': {
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
    item_methods = ['GET', 'PATCH', 'PUT', 'DELETE']
    resource_methods = ['GET', 'POST', 'DELETE']
    privileges = {'POST': 'dictionaries', 'PATCH': 'dictionaries', 'DELETE': 'dictionaries'}


class DictionaryAddWordResource(Resource):
    endpoint_name = 'dictionary_addword'
    url = 'dictionaries/<{0}:dict_id>/addword'.format('regex("[\w,.:_-]+")')
    schema = {'word': {'type': 'string'}}
    datasource = {'source': 'dictionaries'}
    resource_methods = ['POST']
    resource_title = endpoint_name
    privileges = {'POST': 'dictionaries'}


DICTIONARY_FILE = 'file'


class DictionaryUploadResource(Resource):
    schema = base_dictionary_schema
    schema.update({DICTIONARY_FILE: {'type': 'file', 'required': True}})
    datasource = {
        'source': 'dictionaries'
    }
    item_methods = ['PATCH', 'GET', 'DELETE']
    resource_methods = ['POST']
    privileges = {'POST': 'dictionaries', 'PATCH': 'dictionaries'}
