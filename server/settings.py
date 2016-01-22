
import os

APPLICATION_NAME = 'Superdesk'

INSTALLED_APPS = [
    'apps.auth',
    'superdesk.roles',
    'superdesk.sequences',

    'superdesk.users',
    'apps.auth.db',

    'superdesk.upload',
    'superdesk.notification',
    'superdesk.activity',
    'superdesk.vocabularies',
    'apps.comments',

    'superdesk.io',
    'apps.io',
    'superdesk.publish',
    'superdesk.commands',
    'superdesk.locators.locators',

    'apps.auth',
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
    'apps.legal_archive',
    'apps.search',
    'apps.saved_searches',
    'apps.privilege',
    'apps.rules',
    'apps.highlights',
    'apps.publish',
    'apps.publish.formatters',
    'apps.content_filters',
    'apps.dictionaries',
    'apps.duplication',
    'apps.aap.import_text_archive',
    'apps.aap_mm',
    'apps.spellcheck',
    'apps.templates',
    'apps.archived',
    'apps.validators',
    'apps.validate',
    'apps.workspace',
    'apps.macros',

    'superdesk.io.subjectcodes',
    'pa.topics',
    'pa.pa_img',
    'apps.archive_broadcast',
    'apps.keywords',
    'apps.content_types',
    'apps.picture_crop',
]

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

DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES = 'PA'
DEFAULT_PRIORITY_VALUE_FOR_MANUAL_ARTICLES = 5
DEFAULT_URGENCY_VALUE_FOR_MANUAL_ARTICLES = 5

# This value gets injected into NewsML 1.2 and G2 output documents.
NEWSML_PROVIDER_ID = 'pressassociation.com'
ORGANIZATION_NAME = 'Press Association'
ORGANIZATION_NAME_ABBREVIATION = 'PA'

KEYWORDS_PROVIDER = 'Alchemy'
KEYWORDS_BASE_URL = 'http://access.alchemyapi.com/calls'
KEYWORDS_KEY_API = os.environ.get('KEYWORDS_KEY_API', 'ea87a0a0a219d55492ffa706dc878ee03aadc4c7')

AMAZON_CONTAINER_NAME = os.environ.get('AMAZON_CONTAINER_NAME', '')
AMAZON_ACCESS_KEY_ID = os.environ.get('AMAZON_ACCESS_KEY_ID', '')
AMAZON_SECRET_ACCESS_KEY = os.environ.get('AMAZON_SECRET_ACCESS_KEY', '')
AMAZON_REGION = os.environ.get('AMAZON_REGION', 'us-east-1')
AMAZON_SERVE_DIRECT_LINKS = os.environ.get('AMAZON_SERVE_DIRECT_LINKS', False)
AMAZON_S3_USE_HTTPS = os.environ.get('AMAZON_S3_USE_HTTPS', False)

WS_HOST = os.environ.get('WSHOST', '0.0.0.0')
WS_PORT = os.environ.get('WSPORT', '5100')

LOG_SERVER_ADDRESS = os.environ.get('LOG_SERVER_ADDRESS', 'localhost')
LOG_SERVER_PORT = int(os.environ.get('LOG_SERVER_PORT', 5555))

APP_ABSPATH = os.path.abspath(os.path.dirname(__file__))
INIT_DATA_PATH = os.path.join(APP_ABSPATH, 'data')
