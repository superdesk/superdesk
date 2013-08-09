"""
    Superdesk Manager
"""

from app import app
from flask.ext import script

from superdesk import users
from superdesk.io import reuters

manager = script.Manager(app)

@manager.command
def update_ingest():
    """Runs an ingest update."""
    reuters.Service().update(app.data.driver.db, app.config)

@manager.command
def create_user(username, password):
    """Create new user."""
    app.data.driver.db.users.insert({'username': username, 'password': password})

if __name__ == '__main__':
    manager.run()
