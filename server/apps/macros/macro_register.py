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
import sys
import imp
from flask import current_app as app
import macros


def load_macros():
    module = app.config['MACROS_MODULE']
    load_module(module)


def load_module(module):
    """
    It will load the given module
    If the module is loaded before it will reload it
    :param module: name of he module
    """
    try:
        m = sys.modules[module]
        imp.reload(m)
    except AttributeError:
        try:
            importlib.import_module(module)
        except ImportError:
            return
    register_macros()


def register_macros():
    macro_modules = [sys.modules[m] for m in sys.modules.keys()
                     if 'macros.' in m and
                     'callback' in dir(sys.modules[m]) and
                     not m.endswith('_test')
                     and not m.startswith('__')]
    print(macro_modules)

    for macro_module in macro_modules:
        register(name=macro_module.name,
                 label=macro_module.label,
                 shortcut=macro_module.shortcut,
                 callback=macro_module.callback)


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
        load_macros()
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
        self.macros = [macro for macro in self.macros if macro['name'] != kwargs.get('name')]
        self.macros.append(kwargs)


macros = MacroRegister()


def register(**kwargs):
    """Alias for macro.register."""
    macros.register(**kwargs)
