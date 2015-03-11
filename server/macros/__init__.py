"""Here you can import/implement macros.

This module will get reloaded per request to be up to date.

Use `superdesk.macros.macros.register` for registration.
"""
from superdesk.macros import load_module

macros = ['macros.currency',
          'macros.abstract_populator']

for macro in macros:
    load_module(macro)
