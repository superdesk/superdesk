"""Here you can import/implement macros.

This module will get reloaded per request to be up to date.

Use `superdesk.macros.macros.register` for registration.
"""
from superdesk.macros import load_module
import os

macros = [f[:-3] for f in os.listdir(os.path.abspath('macros'))
          if f.endswith('.py')
          and not f.endswith('_test.py')
          and not f.startswith('__')]

for macro in macros:
    load_module('macros.{}'.format(macro))
