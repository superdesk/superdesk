"""Here you can import/implement macros.

This module will get reloaded per request to be up to date.

Use `superdesk.macros.macros.register` for registration.
"""
import sys
import imp
macros = ['macros.currency', 'macros.currencymex']

try:
    already_imported = sorted(sys.modules.keys())
    loaded = False
    for t in already_imported:
        if t in macros:
            m = sys.modules[t]
            imp.reload(m)
            loaded = True
            continue

    if not loaded:
        for m in macros:
            __import__(m)
except Exception as ex:
    pass






