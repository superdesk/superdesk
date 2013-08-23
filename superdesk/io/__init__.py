"""Superdesk IO"""

from reuters import Service
from superdesk import app, mongo

def update_ingest():
    Service().update(mongo.db, app.config)
