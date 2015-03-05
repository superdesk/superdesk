# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import inspect
import importlib

from flask import current_app as app


def load_macros():
    """Import macros modules.

    If module was imported before it will reload it.
    """
    try:
        module = app.config['MACROS_MODULE']
        importlib.import_module(module)
    except ImportError:
        pass


class MacroRegister():
    """Dynamic macros registry.

    Will look for new macros whenever macros are used.
    """

    def __init__(self):
        self.macros = []

    def __iter__(self):
        """Implement for macro in macros."""
        self.index = -1
        load_macros()
        return self

    def __next__(self):
        """Implement for macro in macros."""
        self.index += 1
        try:
            return self.macros[self.index]
        except IndexError:
            raise StopIteration

    def __contains__(self, name):
        """Implement 'name' in macros.

        :param name: macro name
        """
        load_macros()
        return self.find(name) is not None

    def find(self, name):
        """Find a macro by given macro name.

        :param name: macro name
        """
        for macro in self.macros:
            if macro.get('name') == name:
                return macro

    def register(self, **kwargs):
        """Register a new macro.

        :param name: unique macro name, used to identify macro
        :param label: macro label, used by client when listing macros 
        :param callback: macro callback implementing functionality, should use **kwargs to be able to handle new params
        :param shortcut: default client shortcut (witch ctrl)
        :param description: macro description, using callback doctext as default
        """
        kwargs.setdefault('description', inspect.getdoc(kwargs.get('callback')))
        self.macros.append(kwargs)


macros = MacroRegister()


def register(**kwargs):
    """Alias for macro.register."""
    macros.register(**kwargs)
