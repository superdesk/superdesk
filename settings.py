
import os


URL_PREFIX = os.environ.get('SUPERDESK_URL_PREFIX', '')
SERVER_NAME = os.environ.get('SUPERDESK_SERVER_NAME', 'localhost:5000')

BANDWIDTH_SAVER = False

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

XML = False
ETAG = 'etag'
STATUS = 'status'
ISSUES = 'issues'
DATE_CREATED = 'created'
LAST_UPDATED = 'updated'

X_DOMAINS = '*'
X_HEADERS = ['Content-Type', 'Authorization', 'If-Match']

MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'superdesk')
if os.environ.get('MONGOLAB_URI'):
    MONGO_URI = os.environ.get('MONGOLAB_URI')
    SERVER_NAME = 'superdesk-api.herokuapp.com'

ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')
ELASTICSEARCH_INDEX = os.environ.get('ELASTICSEARCH_INDEX', 'superdesk')

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
)

RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

# uncomment to use local file storage
# DEFAULT_FILE_STORAGE = 'superdesk.storage.FileSystemStorage'
# abspath = os.path.abspath(os.path.dirname(__file__))
# UPLOAD_FOLDER = os.path.join(abspath, 'upload')
