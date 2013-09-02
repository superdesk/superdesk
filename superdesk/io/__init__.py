"""Superdesk IO"""

from superdesk import app, mongo
from .reuters import Service

def update_ingest():
    Service().update(mongo.db, app.config)
