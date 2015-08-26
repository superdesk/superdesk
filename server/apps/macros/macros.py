# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import superdesk
from superdesk.errors import SuperdeskApiError
from superdesk.utils import ListCursor
from superdesk.macro_register import macros


def get_public_props(item):
    return {k: v for k, v in item.items() if k != 'callback'}


class MacrosService(superdesk.Service):

    def get(self, req, lookup):
        """Return all registered macros."""
        desk = getattr(req, 'args', {}).get('desk')
        if desk:
            return ListCursor([get_public_props(macro) for macro in macros
                               if desk.upper() in macro.get('desks', [])
                               or macro.get('desks') is None])
        else:
            return ListCursor([get_public_props(macro) for macro in macros])

    def create(self, docs, **kwargs):
        try:
            ids = []
            for doc in docs:
                doc['item'] = self.execute_macro(doc['item'], doc['macro'])
                if doc.get('commit'):
                    item = superdesk.get_resource_service('archive').find_one(req=None, _id=doc['item']['_id'])
                    updates = doc['item'].copy()
                    updates.pop('_id')
                    superdesk.get_resource_service('archive').update(item['_id'], updates, item)
                ids.append(doc['macro'])
            return ids
        except Exception as ex:
            raise SuperdeskApiError.internalError(str(ex))

    def get_macro_by_name(self, macro_name):
        return macros.find(macro_name)

    def execute_macro(self, doc, macro_name):
        macro = self.get_macro_by_name(macro_name)
        return macro['callback'](doc)


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
        'commit': {
            'type': 'boolean',
            'default': False,
        },
    }


def init_app(app):
    MacrosResource('macros', app=app, service=MacrosService())
