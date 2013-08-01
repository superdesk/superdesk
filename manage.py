"""
    Superdesk Manager
"""

from eve import Eve
from eve.utils import config
from flask.ext import script

app = Eve()

from superdesk import users
from superdesk.io import reuters

manager = script.Manager(app)

@manager.command
def update_ingest():
    """Runs an ingest update."""
    reuters.Service().update(app.data.driver.db, config)

@manager.command
def create_user(username, password):
    """Create new user."""
    user = users.create_user(username, password)

if __name__ == '__main__':
    manager.run()
