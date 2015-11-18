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


DICTIONARY_FILE = 'file'


class DictionariesResource(Resource):
    '''
    Dictionaries schema
    '''
    schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'language_id': {
            'type': 'string',
            'required': True
        },
        'content': {
            'type': 'dict',
        },
        'content_list': {
            'type': 'string',
        },
        DICTIONARY_FILE: {
            'type': 'file',
        },
        'user': Resource.rel('users', nullable=True),
        'is_active': {
            'type': 'string',
            'default': 'true',
        },
    }
    item_methods = ['GET', 'PATCH', 'PUT', 'DELETE']
    resource_methods = ['GET', 'POST', 'DELETE']
    privileges = {'POST': 'dictionaries', 'PATCH': 'dictionaries', 'DELETE': 'dictionaries'}
    etag_ignore_fields = ['content', 'content_list']
