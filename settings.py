import os
from datetime import timedelta
import json

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def env(variable, fallback_value=None):
    env_value = os.environ.get(variable, '')
    if len(env_value) == 0:
        return fallback_value
    else:
        if env_value == "__EMPTY__":
            return ''
        else:
            return env_value


XML = False
IF_MATCH = True
BANDWIDTH_SAVER = False
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

APPLICATION_NAME = env('APP_NAME', 'Superdesk')
server_url = urlparse(env('SUPERDESK_URL', 'http://localhost:5000/api'))
CLIENT_URL = env('SUPERDESK_CLIENT_URL', 'http://localhost:9000')
URL_PROTOCOL = server_url.scheme or None
SERVER_NAME = server_url.netloc or None
URL_PREFIX = server_url.path.lstrip('/') or ''
VALIDATION_ERROR_STATUS = 400

CACHE_CONTROL = 'max-age=0, no-cache'

X_DOMAINS = '*'
X_MAX_AGE = 24 * 3600
X_HEADERS = ['Content-Type', 'Authorization', 'If-Match']


MONGO_DBNAME = env('MONGO_DBNAME', 'superdesk')
if env('MONGOLAB_URI'):
    MONGO_URI = env('MONGOLAB_URI')
elif env('MONGODB_PORT'):
    MONGO_URI = '{0}/{1}'.format(env('MONGODB_PORT').replace('tcp:', 'mongodb:'), MONGO_DBNAME)

LEGAL_ARCHIVE_DBNAME = env('LEGAL_ARCHIVE_DBNAME', 'legal_archive')
if env('LEGAL_ARCHIVE_URI'):
    LEGAL_ARCHIVE_URI = env('LEGAL_ARCHIVE_URI')
elif env('LEGAL_ARCHIVEDB_PORT'):
    LEGAL_ARCHIVE_URI = '{0}/{1}'.format(env('LEGAL_ARCHIVEDB_PORT').replace('tcp:', 'mongodb:'),
                                         LEGAL_ARCHIVE_DBNAME)

ELASTICSEARCH_URL = env('ELASTICSEARCH_URL', 'http://localhost:9200')
ELASTICSEARCH_INDEX = env('ELASTICSEARCH_INDEX', 'superdesk')
if env('ELASTIC_PORT'):
    ELASTICSEARCH_URL = env('ELASTIC_PORT').replace('tcp:', 'http:')

REDIS_URL = env('REDIS_URL', 'redis://localhost:6379')
if env('REDIS_PORT'):
    REDIS_URL = env('REDIS_PORT').replace('tcp:', 'redis:')
BROKER_URL = env('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', REDIS_URL)
CELERY_ALWAYS_EAGER = (env('CELERY_ALWAYS_EAGER', False) == 'True')
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']  # it's using pickle when in eager mode

CELERYBEAT_SCHEDULE = {
    'fetch_ingest': {
        'task': 'superdesk.io.fetch_ingest',
        # there is internal schedule for updates per provider,
        # so this is mininal interval when an update can occur
        'schedule': timedelta(seconds=10),
        'options': {'expires': 19}
    },
    'auth_session_purge': {
        'task': 'apps.auth.session_purge',
        'schedule': timedelta(minutes=30)
    },
    'spike_purge': {
        'task': 'apps.archive.spike_purge',
        'schedule': timedelta(minutes=60)
    }
}

SENTRY_DSN = env('SENTRY_DSN')
SENTRY_INCLUDE_PATHS = ['superdesk']

INSTALLED_APPS = [
    'apps.auth',
    'apps.users',
    'superdesk.upload',
    'superdesk.notification',
    'superdesk.activity',
    'superdesk.comments',
    'superdesk.storage.amazon.import_from_amazon',

    'superdesk.io',
    'superdesk.io.subjectcodes',
    'superdesk.io.reuters',
    'superdesk.io.aap',
    'superdesk.io.afp',

    'apps.archive',
    'apps.stages',
    'apps.desks',
    'apps.planning',
    'apps.coverages',
    'apps.tasks',
    'apps.preferences',
    'apps.spikes',
    'apps.groups',
    'apps.prepopulate',
    'apps.vocabularies',
    'apps.legal_archive',
    'apps.search',
    'apps.packages',
    'apps.privilege',
]

RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']
RETURN_MEDIA_AS_BASE64_STRING = False

AMAZON_CONTAINER_NAME = env('AMAZON_CONTAINER_NAME', '')
AMAZON_ACCESS_KEY_ID = env('AMAZON_ACCESS_KEY_ID', '')
AMAZON_SECRET_ACCESS_KEY = env('AMAZON_SECRET_ACCESS_KEY', '')
AMAZON_REGION = env('AMAZON_REGION', '')


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
RESET_PASSWORD_TOKEN_TIME_TO_LIVE = int(env('RESET_PASS_TTL', 1))  # The number of days a token is valid
# The number of days an activation token is valid
ACTIVATE_ACCOUNT_TOKEN_TIME_TO_LIVE = int(env('ACTIVATE_TTL', 7))

# email server
MAIL_SERVER = env('MAIL_SERVER', 'smtp.googlemail.com')
MAIL_PORT = int(env('MAIL_PORT', 465))
MAIL_USE_TLS = json.loads(env('MAIL_USE_TLS', 'False').lower())
MAIL_USE_SSL = json.loads(env('MAIL_USE_SSL', 'False').lower())
MAIL_USERNAME = env('MAIL_USERNAME', 'admin@sourcefabric.org')
MAIL_PASSWORD = env('MAIL_PASSWORD', '')
ADMINS = [MAIL_USERNAME]

# LDAP settings
LDAP_SERVER = env('LDAP_SERVER', '')  # Ex: ldap://sourcefabric.org
LDAP_SERVER_PORT = env('LDAP_SERVER_PORT', 389)

# Fully Qualified Domain Name. Ex: sourcefabric.org
LDAP_FQDN = env('LDAP_FQDN', '')

# LDAP_BASE_FILTER limit the base filter to the security group. Ex: OU=Superdesk Users,dc=sourcefabric,dc=org
LDAP_BASE_FILTER = env('LDAP_BASE_FILTER', '')

# change the user depending on the LDAP directory structure
LDAP_USER_FILTER = env('LDAP_USER_FILTER', "(&(objectCategory=user)(objectClass=user)(sAMAccountName={}))")

# LDAP User Attributes to fetch. Keys would be LDAP Attribute Name and Value would be Supderdesk Model Attribute Name
LDAP_USER_ATTRIBUTES = {'givenName': 'first_name', 'sn': 'last_name', 'displayName': 'display_name',
                        'mail': 'email', 'ipPhone': 'phone'}

if LDAP_SERVER:
    INSTALLED_APPS.append('apps.auth.ldap')
else:
    INSTALLED_APPS.append('apps.auth.db')

SUPERDESK_TESTING = (env('SUPERDESK_TESTING', 'false').lower() == 'true')

# The number of minutes since the last update of the Mongo auth object after which it will be deleted
SESSION_EXPIRY_MINUTES = 240

# The number of minutes before spiked items purged
SPIKE_EXPIRY_MINUTES = 300
