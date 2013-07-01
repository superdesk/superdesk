from flask import current_app
from app import app, connect_db

from superdesk.io import reuters


# try to run within app context
connect_db()
service = reuters.Service()
service.update()

