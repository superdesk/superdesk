
import os
from datetime import timedelta
import json

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

XML = False
IF_MATCH = False
BANDWIDTH_SAVER = False
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

server_url = urlparse(os.environ.get('SUPERDESK_URL', 'http://localhost:5000'))
URL_PROTOCOL = server_url.scheme or None
SERVER_NAME = server_url.netloc or None
URL_PREFIX = server_url.path.lstrip('/') or ''
VALIDATION_ERROR_STATUS = 400

CACHE_CONTROL = 'max-age=0, no-cache'

X_DOMAINS = '*'
X_HEADERS = ['Content-Type', 'Authorization', 'If-Match']

MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'superdesk')
if os.environ.get('MONGOLAB_URI'):
    MONGO_URI = os.environ.get('MONGOLAB_URI')

ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')
ELASTICSEARCH_INDEX = os.environ.get('ELASTICSEARCH_INDEX', 'superdesk')

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
CELERY_ALWAYS_EAGER = (os.environ.get('CELERY_ALWAYS_EAGER', False) == 'True')
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']  # it's using pickle when in eager mode

CELERYBEAT_SCHEDULE = {
    'fetch_ingest': {
        'task': 'apps.io.fetch_ingest',
        'schedule': timedelta(minutes=5)
    }
}

REUTERS_USERNAME = os.environ.get('REUTERS_USERNAME', '')
REUTERS_PASSWORD = os.environ.get('REUTERS_PASSWORD', '')

SENTRY_DSN = os.environ.get('SENTRY_DSN')
SENTRY_INCLUDE_PATHS = ['superdesk']

INSTALLED_APPS = (
    'superdesk.celery_app',  # this must be the first one
    'apps.io',
    'apps.auth',
    'apps.users',
    'apps.archive',
    'apps.activity',
    'apps.upload',
    'apps.desks',
    'superdesk.storage.amazon.import_from_amazon',
    'superdesk.notification',
    'apps.planning',
    'apps.coverages',
    'apps.tasks',
)

RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']
RETURN_MEDIA_AS_BASE64_STRING = False

AMAZON_CONTAINER_NAME = os.environ.get('AMAZON_CONTAINER_NAME', '')
AMAZON_ACCESS_KEY_ID = os.environ.get('AMAZON_ACCESS_KEY_ID', '')
AMAZON_SECRET_ACCESS_KEY = os.environ.get('AMAZON_SECRET_ACCESS_KEY', '')
AMAZON_REGION = os.environ.get('AMAZON_REGION', '')


RENDITIONS = {
    'picture': {
        'thumbnail': {'width': 220, 'height': 120},
        'viewImage': {'width': 640, 'height': 640},
        'baseImage': {'width': 1400, 'height': 1400},
    },
    'avatar': {
        'thumbnail': {'width': 60, 'height': 60},
        'viewImage': {'width': 200, 'height': 200},
    }
}

SERVER_DOMAIN = 'localhost'

BCRYPT_GENSALT_WORK_FACTOR = 12
RESET_PASSWORD_TOKEN_TIME_TO_LIVE = 24  # The number of hours a token is valid

# email server
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
MAIL_USE_TLS = json.loads(os.environ.get('MAIL_USE_TLS', 'False').lower())
MAIL_USE_SSL = json.loads(os.environ.get('MAIL_USE_SSL', 'True').lower())
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'admin@sourcefabric.org')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'admin-password')
ADMINS = [MAIL_USERNAME]
