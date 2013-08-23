"""Superdesk Manager"""

from superdesk import app
from flask.ext import script

import superdesk.io
import superdesk.users

manager = script.Manager(app)

@manager.option('--username', '-u', dest='username')
@manager.option('--password', '-p', dest='password')
def create_user(username, password):
    """Create new user"""
    return superdesk.users.create_user(username, password)

@manager.command
def update_ingest():
    """Update ingest"""
    return superdesk.io.update_ingest()

if __name__ == '__main__':
    manager.run()
