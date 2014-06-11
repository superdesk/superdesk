"""Superdesk Manager"""

import superdesk
from flask.ext.script import Manager
from app import get_app

app = get_app()
manager = Manager(app)

if __name__ == '__main__':
    manager.run(superdesk.COMMANDS)
