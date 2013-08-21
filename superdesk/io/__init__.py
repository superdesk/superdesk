"""Superdesk IO"""

from reuters import Service
from app import app

def update_ingest():
    Service().update(app.data.driver.db, app.config)
