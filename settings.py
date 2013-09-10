
import os

MONGO_DBNAME = os.environ.get('MONGOHQ_URL', 'superdesk')

ELASTIC_INDEX = os.environ.get('ELASTIC_INDEX', 'superdesk')

SERVER_NAME = 'localhost:5000'
