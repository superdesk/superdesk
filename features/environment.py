from superdesk import tests
from superdesk.io.tests import setup_providers, teardown_providers
from settings import LDAP_SERVER
from flask import json


readonly_fields = ['display_name', 'password', 'phone', 'first_name', 'last_name']


def before_all(context):
    tests.setup(context)


def before_feature(context, feature):
    if 'dbauth' in feature.tags and LDAP_SERVER:
        feature.mark_skipped()


def before_scenario(context, scenario):
    config = {}
    if scenario.status != 'skipped' and 'notesting' in scenario.tags:
        config['TESTING'] = False

    tests.setup(context, config)
    context.headers = [
        ('Content-Type', 'application/json'),
        ('Origin', 'localhost')
    ]

    if 'dbauth' in scenario.tags and LDAP_SERVER:
        scenario.mark_skipped()

    if scenario.status != 'skipped' and 'auth' in scenario.tags:
        tests.setup_auth_user(context)

    if scenario.status != 'skipped' and 'provider' in scenario.tags:
        setup_providers(context)

    if scenario.status != 'skipped' and 'notification' in scenario.tags:
        tests.setup_notification(context)


def after_scenario(context, scenario):
    if 'provider' in scenario.tags:
        teardown_providers(context)

    if 'notification' in scenario.tags:
        tests.teardown_notification(context)


def before_step(context, step):
    if LDAP_SERVER and step.text:
        step_text_json = json.loads(step.text)
        step_text_json = {k: step_text_json[k] for k in step_text_json.keys() if k not in readonly_fields} \
            if isinstance(step_text_json, dict) else \
            [{k: json_obj[k] for k in json_obj.keys() if k not in readonly_fields} for json_obj in step_text_json]

        step.text = json.dumps(step_text_json)
