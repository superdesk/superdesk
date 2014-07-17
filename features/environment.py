from superdesk import tests


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
        tests.setup_providers(context)


def after_scenario(context, scenario):
    if 'provider' in scenario.tags:
        tests.teardown_providers(context)
