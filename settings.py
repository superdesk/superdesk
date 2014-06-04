
import os
from urllib.parse import urlparse

XML = False
IF_MATCH = False
BANDWIDTH_SAVER = False
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'


server_url = urlparse(os.environ.get('SUPERDESK_URL', 'http://localhost:5000'))
URL_PROTOCOL = server_url.scheme or None
SERVER_NAME = server_url.netloc or None
URL_PREFIX = server_url.path.lstrip('/') or ''

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
CELERY_ALWAYS_EAGER = True


INSTALLED_APPS = (
    'superdesk.io',
    'superdesk.auth',
    'superdesk.users',
    'superdesk.user_roles',
    'superdesk.items',
    'superdesk.activity',
    'superdesk.upload',
    'superdesk.sessions',
    'superdesk.desks',
    'superdesk.subjectcodes',
    'superdesk.archive_ingest',
)

RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']
RETURN_MEDIA_AS_BASE64_STRING = False

# Amazon S3
# AMAZON_CONTAINER_NAME = 'superdesk-test'  # To be replaced with a proper container
# AMAZON_ACCESS_KEY_ID = 'dummy-key'
# AMAZON_SECRET_ACCESS_KEY = 'dummy-access-key'

# allowed: 's3' 's3_us_west' 's3_eu_west' 's3_ap_southeast' 's3_ap_northeast'
# AMAZON_REGION = 's3-eu-west-1'

RENDITIONS = {
    'picture': {
        'thumbnail': {'width': 220, 'height': 120},
        'viewImage': {'width': 640, 'height': 640},
        'baseImage': {'width': 1400, 'height': 1400},
    }
}

SERVER_DOMAIN = 'localhost'

# uncomment to use local file storage
# DEFAULT_FILE_STORAGE = 'superdesk.storage.FileSystemStorage'
abspath = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(abspath, 'upload')
