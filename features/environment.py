from superdesk import tests


def before_all(context):
    tests.setup(context)


def before_scenario(context, scenario):
    tests.setup(context)
    context.headers = [
        ('Content-Type', 'application/json'),
        ('Origin', 'localhost')
    ]
    if 'auth' in scenario.tags:
        tests.setup_auth_user(context)
