from superdesk import tests
from superdesk.io.tests import setup_providers, teardown_providers


def before_all(context):
    tests.setup(context)


def before_scenario(context, scenario):
    config = {}
    tests.setup(context, config)
    context.headers = [
        ('Content-Type', 'application/json'),
        ('Origin', 'localhost')
    ]

    if 'auth' in scenario.tags:
        tests.setup_auth_user(context)

    if 'provider' in scenario.tags:
        setup_providers(context)

    if 'notification' in scenario.tags:
        tests.setup_notification(context)


def after_scenario(context, scenario):
    if 'provider' in scenario.tags:
        teardown_providers(context)

    if 'notification' in scenario.tags:
        tests.teardown_notification(context)
