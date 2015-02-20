# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import superdesk

from superdesk.utils import ListCursor
from superdesk.macros import macros


def get_public_props(item):
    return {k: v for k, v in item.items() if k != 'callback'}


class MacrosService(superdesk.Service):

    def get(self, req, lookup):
        """Return all registered macros."""
        return ListCursor([get_public_props(macro) for macro in macros])

    def create(self, docs, **kwargs):
        ids = []
        for doc in docs:
            macro = macros.find(doc['macro'])
            doc['item'] = macro['callback'](doc.get('item'))
            ids.append(macro['name'])
        return ids


class MacrosResource(superdesk.Resource):
    resource_methods = ['GET', 'POST']
    item_methods = []
    privileges = {'POST': 'archive'}

    schema = {
        'macro': {
            'type': 'string',
            'required': True,
            'allowed': macros
        },
        'item': {
            'type': 'dict',
        },
    }


def init_app(app):
    MacrosResource('macros', app=app, service=MacrosService())
