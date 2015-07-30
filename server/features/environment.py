# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
from superdesk import tests
from superdesk.io.tests import setup_providers, teardown_providers
from settings import LDAP_SERVER
from features.steps.steps import get_macro_path
from flask import json
from apps.vocabularies.command import VocabulariesPopulateCommand


readonly_fields = ['display_name', 'password', 'phone', 'first_name', 'last_name']


def before_all(context):
    tests.setup(context)
    os.environ['BEHAVE_TESTING'] = '1'


def before_feature(context, feature):
    if 'dbauth' in feature.tags and LDAP_SERVER:
        feature.mark_skipped()

    if 'ldapauth' in feature.tags and not LDAP_SERVER:
        feature.mark_skipped()


def before_scenario(context, scenario):
    config = {}
    if scenario.status != 'skipped' and 'notesting' in scenario.tags:
        config['SUPERDESK_TESTING'] = False

    tests.setup(context, config)
    context.headers = [
        ('Content-Type', 'application/json'),
        ('Origin', 'localhost')
    ]

    if 'dbauth' in scenario.tags and LDAP_SERVER:
        scenario.mark_skipped()

    if 'ldapauth' in scenario.tags and not LDAP_SERVER:
        scenario.mark_skipped()

    if scenario.status != 'skipped' and 'auth' in scenario.tags:
        tests.setup_auth_user(context)

    if scenario.status != 'skipped' and 'provider' in scenario.tags:
        setup_providers(context)

    if scenario.status != 'skipped' and 'vocabulary' in scenario.tags:
        with context.app.app_context():
            cmd = VocabulariesPopulateCommand()
            filename = os.path.join(os.path.abspath(os.path.dirname("features/steps/fixtures/")), "vocabularies.json")
            cmd.run(filename)

    if scenario.status != 'skipped' and 'notification' in scenario.tags:
        tests.setup_notification(context)


def after_scenario(context, scenario):
    if 'provider' in scenario.tags:
        teardown_providers(context)

    if 'notification' in scenario.tags:
        tests.teardown_notification(context)

    if 'clean' in scenario.tags:
        try:
            os.remove(get_macro_path('behave_macro.py'))
            os.remove(get_macro_path('validate_headline_macro.py'))
        except:
            pass


def before_step(context, step):
    if LDAP_SERVER and step.text:
        try:
            step_text_json = json.loads(step.text)
            step_text_json = {k: step_text_json[k] for k in step_text_json.keys() if k not in readonly_fields} \
                if isinstance(step_text_json, dict) else \
                [{k: json_obj[k] for k in json_obj.keys() if k not in readonly_fields} for json_obj in step_text_json]

            step.text = json.dumps(step_text_json)
        except:
            pass
