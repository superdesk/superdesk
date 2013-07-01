"""
    Superdesk Manager
"""

from flask.ext import script

from superdesk.io import reuters
from superdesk import app

manager = script.Manager(app)

@manager.command
def update_ingest():
    """Runs an ingest update."""
    connect_db()
    reuters.Service().update()

if __name__ == '__main__':
    manager.run()
