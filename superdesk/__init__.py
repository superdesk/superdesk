"""
Superdesk server app
"""

import importlib
import eve.io.mongo
import settings

class Superdesk(eve.io.mongo.Mongo):
    pass

db = None
DOMAIN = {}

for app_name in settings.INSTALLED_APPS:
    importlib.import_module(app_name)
