from .commands.update_ingest import ingest_items
from .reuters_mock import setup_reuters_mock, teardown_reuters_mock
from .reuters import ReutersUpdateService


def setup_providers(context):
    app = context.app
    context.providers = {}
    context.provider_services = {}
    context.ingest_items = ingest_items
    with app.test_request_context():
        if not app.config['REUTERS_USERNAME'] or not app.config['REUTERS_PASSWORD']:
            # no reuters credential available so use reuters mock
            app.config['REUTERS_USERNAME'] = 'no_username'
            app.config['REUTERS_PASSWORD'] = 'no_password'
            setup_reuters_mock(context)

        provider = {'name': 'reuters',
                    'type': 'reuters',
                    'config': {'username': app.config['REUTERS_USERNAME'],
                               'password': app.config['REUTERS_PASSWORD']
                               }
                    }

        result = app.data.insert('ingest_providers', [provider])
        context.providers['reuters'] = result[0]
        context.provider_services['reuters'] = ReutersUpdateService()


def teardown_providers(context):
    teardown_reuters_mock(context)
