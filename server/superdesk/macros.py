
import inspect
import pkgutil
import importlib

from flask import current_app as app
from superdesk import logger


modules = {}


def load_modules():
    """Import all modules within configured MACROS_PATH directory.

    If module was imported before it will be reloaded.
    """
    path = app.config['MACROS_PATH']
    logger.info('loading macros from "%s"' % path)
    for loader, name, is_pkg in pkgutil.iter_modules([path]):
        if name.endswith('test'):
            continue
        if not modules.get(name):
            modules[name] = loader.find_module(name).load_module(name)
        else:
            modules[name] = importlib.reload(modules[name])


class MacroRegister():
    """Dynamic macros registry.

    Will look for new macros whenever macros are iterated.

    Also supports `name in macros` check.
    """

    def __init__(self):
        self.macros = []

    def __iter__(self):
        """for macro in macros"""
        self.index = -1
        load_modules()
        return self

    def __next__(self):
        """for macro in macros"""
        self.index += 1
        try:
            return self.macros[self.index]
        except IndexError:
            raise StopIteration

    def __len__(self):
        """len(macros)"""
        return len(self.macros)

    def __contains__(self, name):
        """'name' in macros"""
        load_modules()
        return self.find(name) is not None

    def find(self, name):
        for macro in self.macros:
            if macro.get('name') == name:
                return macro

    def register(self, **kwargs):
        kwargs.setdefault('description', inspect.getdoc(kwargs.get('callback')))
        self.macros.append(kwargs)


macros = MacroRegister()


def register(**kwargs):
    """Register a macro."""
    macros.register(**kwargs)
