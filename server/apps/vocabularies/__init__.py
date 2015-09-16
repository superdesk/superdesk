# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


def filter_inactive_vocabularies(item):
    """
    Filters out inactive vocabularies from item and each vocabulary will have only name and value properties.
    """

    vocabulary = item['items']
    active_vocs = ({k: voc[k] for k in voc.keys() if k != 'is_active'}
                   for voc in vocabulary if voc.get('is_active', True))

    item['items'] = list(active_vocs)


def init_app(app):
    endpoint_name = 'vocabularies'
    service = VocabulariesService(endpoint_name, backend=superdesk.get_backend())
    VocabulariesResource(endpoint_name, app=app, service=service)

    service = KeywordsVocabularyService(KeywordsVocabularyResource.endpoint_name, backend=superdesk.get_backend())
    KeywordsVocabularyResource(KeywordsVocabularyResource.endpoint_name, app=app, service=service)

    superdesk.privilege(name='vocabulary_keywords', label='Manage Keywords',
                        description='Manage Keywords Vocabulary')


import superdesk

from .vocabularies import VocabulariesResource, VocabulariesService
from .keywords import KeywordsVocabularyResource, KeywordsVocabularyService
from .command import VocabulariesPopulateCommand  # noqa
