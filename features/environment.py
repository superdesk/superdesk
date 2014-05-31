from superdesk import tests
from app import setup_amazon


def before_all(context):
    tests.setup(context)


def before_scenario(context, scenario):
    config = {}
    if 'amazon' in scenario.tags:
        setup_amazon(config)

    tests.setup(context, config)
    context.headers = [
        ('Content-Type', 'application/json'),
        ('Origin', 'localhost')
    ]
    if 'auth' in scenario.tags:
        tests.setup_auth_user(context)
