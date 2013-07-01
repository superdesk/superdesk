import os

DEBUG = False

DB_NAME = os.environ.get('MONGOHQ_URL', 'superdesk')
