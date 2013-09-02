
import os

MONGO_DBNAME = os.environ.get('MONGOHQ_URL', 'superdesk')

SERVER_NAME = 'localhost:5000'

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')
MEDIA_URL = 'http://localhost:8000/'
