from .commands.update_ingest import ingest_items
from .reuters_mock import setup_reuters_mock, teardown_reuters_mock
from .reuters import ReutersIngestService
from .aap import AAPIngestService
import superdesk


def setup_providers(context):
    app = context.app
    context.providers = {}
    context.provider_services = {}
    context.ingest_items = ingest_items
    with app.test_request_context(app.config['URL_PREFIX']):
        rule_sets = {'name': 'reuters_rule_sets',
                     'rules': [
                         {"old": "@", "new": ""},
                     ]}

        result = superdesk.get_resource_service('rule_sets').post([rule_sets])

        app.config['REUTERS_USERNAME'] = 'no_username'
        app.config['REUTERS_PASSWORD'] = 'no_password'
        setup_reuters_mock(context)
        providers = [
            {'name': 'reuters', 'type': 'reuters', 'source': 'reuters', 'is_closed': False, 'rule_set': result[0],
             'config': {'username': app.config['REUTERS_USERNAME'],
                        'password': app.config['REUTERS_PASSWORD']}},
            {'name': 'AAP', 'type': 'aap', 'source': 'AAP Ingest', 'is_closed': False}
        ]

        result = superdesk.get_resource_service('ingest_providers').post(providers)
        context.providers['reuters'] = result[0]
        context.provider_services['reuters'] = ReutersIngestService()
        context.provider_services['aap'] = AAPIngestService()


def teardown_providers(context):
    teardown_reuters_mock(context)
