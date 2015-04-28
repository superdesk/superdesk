# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.utils import date_to_str
from flask import current_app as app
import json
import os

from publicapi.behave_setup import drop_elastic, drop_mongo
from superdesk import get_resource_service
import superdesk
from superdesk.services import BaseService
from superdesk.utc import utcnow
from superdesk.errors import SuperdeskApiError
from contextlib import contextmanager


def apply_placeholders(placeholders, text):
    if not placeholders or not text:
        return text
    for tag, value in placeholders.items():
        text = text.replace(tag, value)
    return text


@contextmanager
def open_with_report(file, mode='r', buffering=-1, encoding=None, errors=None):
    try:
        yield open(file, mode, buffering, encoding, errors)
    except FileNotFoundError:
        raise SuperdeskApiError.notFoundError('Prepopulate profile not found')


def prepopulate_data(file_name):
    placeholders = {'NOW()': date_to_str(utcnow())}
    file = os.path.join(superdesk.app.config.get('APP_ABSPATH'), 'prepopulate', 'prepopulate-data', file_name)
    with open_with_report(file, 'rt', encoding='utf8') as app_prepopulation:
        json_data = json.load(app_prepopulation)
        for item in json_data:
            service = get_resource_service(item.get('resource', None))
            id_name = item.get('id_name', None)
            text = json.dumps(item.get('data', None))
            text = apply_placeholders(placeholders, text)
            data = json.loads(text)
            if item.get('resource'):
                app.data.mongo._mongotize(data, item.get('resource'))
            ids = service.post([data])
            if not ids:
                raise Exception()
            if id_name:
                placeholders[id_name] = str(ids[0])


class PrepopulateService(BaseService):
    def create(self, docs, **kwargs):
        for doc in docs:
            if doc.get('remove_first'):
                drop_elastic(superdesk.app)
                drop_mongo(superdesk.app)
            prepopulate_data(doc.get('profile') + '.json')
        return ['OK']
