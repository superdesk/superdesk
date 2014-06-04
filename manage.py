"""Superdesk Manager"""

import superdesk
from flask.ext.script import Manager
from app import get_app, setup_amazon

config = {}
setup_amazon(config)
app = get_app(config=config)
manager = Manager(app)

if __name__ == '__main__':
    manager.run(superdesk.COMMANDS)
