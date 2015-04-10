# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from apps.dictionaries.resource import DictionariesResource, DictionaryUploadResource,\
    DictionaryAddWordResource
from apps.dictionaries.service import DictionaryUploadService,\
    DictionaryAddWordService
from superdesk.services import BaseService


def init_app(app):
    endpoint_name = 'dictionaries'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    DictionariesResource(endpoint_name, app=app, service=service)

    endpoint_name = 'dictionary_upload'
    service = DictionaryUploadService(endpoint_name, backend=superdesk.get_backend())
    DictionaryUploadResource(endpoint_name, app=app, service=service)

    endpoint_name = 'dictionaries_addword'
    service = DictionaryAddWordService(endpoint_name, backend=superdesk.get_backend())
    DictionaryAddWordResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='dictionaries', label='Dictionaries List Management',
                        description='User can manage dictionaries lists.')
