
import inspect
import pkgutil
import importlib

from flask import current_app as app

_macros = []
modules = {}


def register(**kwargs):
    """Register a macro."""
    kwargs.setdefault('description', inspect.getdoc(kwargs.get('callback')))
    _macros.append(kwargs)


def load_modules():
    """Import all modules within configured MACROS_PATH directory.

    If module was imported before it will be reloaded.
    """
    with app.app_context():
        path = app.config['MACROS_PATH']
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

    def __iter__(self):
        self.index = -1
        load_modules()
        return self

    def __contains__(self, item):
        return self.find(item) is not None

    def find(self, name):
        for macro in _macros:
            if macro.get('name') == name:
                return macro

    def __next__(self):
        self.index += 1
        try:
            return _macros[self.index]
        except IndexError:
            raise StopIteration


macros = MacroRegister()
