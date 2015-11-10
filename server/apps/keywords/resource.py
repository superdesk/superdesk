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


class KeywordsResource(Resource):
    '''
    Keywords schema
    '''
    schema = {
        'text': {
            'type': 'string',
            'required': True
        },
        'keywords': {
            'type': 'list',
            'required': False,
            'schema': {
                'type': 'dict',
                'schema': {
                    'text': {'type': 'string', 'required': True, 'empty': False},
                    'relevance': {'type': 'string', 'required': True},
                }
            }
        }
    }
    item_methods = []
    resource_methods = ['POST']
    privileges = {'POST': 'archive'}
