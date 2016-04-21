"""Here you can import/implement macros.

This module will get reloaded per request to be up to date.

Use `superdesk.macro_register.macros.register` for registration.
"""

import os
import sys
import imp
import importlib

macro_replacement_fields = {'body_html', 'body_text', 'abstract', 'headline', 'slugline', 'description_text'}
macros_folder = os.path.realpath(os.path.dirname(__file__))

macros = [f[:-3] for f in os.listdir(macros_folder)
          if f.endswith('.py') and not f.endswith('_test.py') and not f.startswith('__')]

for macro in macros:
    try:
        module = 'ntb.macros.{}'.format(macro)
        if module in sys.modules.keys():
            m = sys.modules[module]
            imp.reload(m)
        else:
            importlib.import_module(module)
    except:
        pass
