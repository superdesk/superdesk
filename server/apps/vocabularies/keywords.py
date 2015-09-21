# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json

import logging

from eve.utils import config
from apps.vocabularies import filter_inactive_vocabularies
from superdesk import Resource, get_resource_service

from superdesk.errors import SuperdeskApiError
from superdesk.resource import build_custom_hateoas
from superdesk.services import BaseService
from superdesk.utils import ListCursor

logger = logging.getLogger(__name__)

_hateoas = {'self': {'title': 'vocabulary_keywords', 'href': '/vocabulary/keywords/{_id}'}}

ID_FIELD_VALUE = 'keywords'

VOCABULARY = 'items'

NAME = 'name'

VALUE = 'value'

ACTIVE = 'is_active'


class KeywordsVocabularyResource(Resource):
    """
    Resource class for handling Keywords Vocabulary. The keywords are saved as a document with identifier "keywords"
    in "vocabularies" collection.
    """

    endpoint_name = 'vocabulary_keywords'
    resource_title = endpoint_name

    schema = {
        'name': {
            'type': 'string',
            'required': True,
        },
        'value': {
            'type': 'string',
            'required': True
        },
        'is_active': {
            'type': 'boolean',
            'default': True
        }
    }
    datasource = {'source': 'vocabularies', 'projection': {VOCABULARY: 1}}

    url = "vocabulary/keywords"
    item_url = 'regex("[\w]+")'

    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH', 'DELETE']

    privileges = {'POST': 'vocabulary_keywords', 'PATCH': 'vocabulary_keywords', 'DELETE': 'vocabulary_keywords'}


class KeywordsVocabularyService(BaseService):
    """
    Service class having methods to manage the "keywords" document in "vocabularies" collection. The keywords will be in
    "items" property of the document. So, overriding the CRUD related methods from BaseService to mimic as if the
    operations are being done on document itself.
    """

    def get(self, req, lookup):
        keywords_vocabulary = self._get_vocabulary()

        if keywords_vocabulary:
            if req and req.args and req.args.get('where'):
                where_clause = req.args.get('where')
                lookup = json.loads(where_clause)

                if VALUE in lookup:
                    keyword = self._find_keyword(lookup[VALUE], keywords_vocabulary[VOCABULARY])
                    keywords_vocabulary[VOCABULARY] = [keyword]
                    if not keyword:
                        raise SuperdeskApiError.notFoundError(message='Keyword {} not found'.format(where_clause))
                elif NAME in lookup:
                    keyword = self._find_keyword(lookup[NAME], keywords_vocabulary[VOCABULARY],
                                                 property_to_match=NAME)
                    keywords_vocabulary[VOCABULARY] = [keyword]
                    if not keyword:
                        raise SuperdeskApiError.notFoundError(message='Keyword {} not found'.format(where_clause))
                elif lookup.get(ACTIVE, False):
                    filter_inactive_vocabularies(keywords_vocabulary)

            for keyword in keywords_vocabulary[VOCABULARY]:
                self._copy_defaults(keyword, keywords_vocabulary)

        return ListCursor(keywords_vocabulary[VOCABULARY]) if keywords_vocabulary else None

    def find_one(self, req, **lookup):
        keywords_vocabulary = self._get_vocabulary()

        if keywords_vocabulary:
            keyword = self._find_keyword(lookup[config.ID_FIELD], keywords_vocabulary[VOCABULARY],
                                         property_to_match=NAME)

            if keyword:
                self._copy_defaults(keyword, keywords_vocabulary)
                return keyword

        return None

    def create(self, docs, **kwargs):
        keywords_vocabulary = self._get_vocabulary()
        insert = False

        if keywords_vocabulary:
            keywords = keywords_vocabulary[VOCABULARY].copy()
        else:
            insert = True
            keywords = []
            keywords_vocabulary = {config.ID_FIELD: ID_FIELD_VALUE, VOCABULARY: keywords}

        for doc in docs:
            keyword = self._find_keyword(doc[VALUE], keywords_vocabulary[VOCABULARY])
            if keyword:
                if keyword[ACTIVE]:
                    raise SuperdeskApiError.badRequestError('Keyword with name {} already exists'.format(keyword[NAME]))

                keyword[ACTIVE] = True
            else:
                keyword = {NAME: doc[NAME], VALUE: doc[VALUE], ACTIVE: True}
                keywords.append(keyword)

        if insert:
            get_resource_service('vocabularies').create([keywords_vocabulary])
        else:
            get_resource_service('vocabularies').update(ID_FIELD_VALUE, {VOCABULARY: keywords}, keywords_vocabulary)

        return [keywords_vocabulary[config.ID_FIELD]]

    def update(self, id, updates, original):
        keywords_vocabulary, keywords, original_keyword = self._find_by_name(original[NAME])

        original_keyword[NAME] = updates[NAME]
        original_keyword[VALUE] = updates[VALUE]

        updated = {VOCABULARY: keywords, config.LAST_UPDATED: updates[config.LAST_UPDATED]}
        get_resource_service('vocabularies').update(ID_FIELD_VALUE, updated, original)

        updates[config.ETAG] = updated[config.ETAG]

    def delete(self, lookup=None):
        vocabulary, keywords, keyword = self._find_by_name(lookup[config.ID_FIELD])

        keyword[ACTIVE] = False
        get_resource_service('vocabularies').update(ID_FIELD_VALUE, {VOCABULARY: keywords}, vocabulary)

    def _find_by_name(self, name):
        """
        Fetches keywords document from vocabularies collection and searches for keyword in the keywords document using
        the passed name.

        :param name:
        :raises: SuperdeskApiError.notFoundError() when keyword using passed name not found or if found and inactive.
        :return: keywords document in the vocabulary, keywords['items'], keyword
        """

        keywords_vocabulary = self._get_vocabulary()
        keywords = keywords_vocabulary[VOCABULARY].copy()
        original_keyword = self._find_keyword(name, keywords, property_to_match=NAME)

        if not original_keyword or not original_keyword[ACTIVE]:
            raise SuperdeskApiError.notFoundError('Keyword with name {} not found'.format(name))

        return keywords_vocabulary, keywords, original_keyword

    def _get_vocabulary(self):
        """
        Fetches a document from vocabularies collection where document['_id'] == 'keywords'
        """

        return get_resource_service('vocabularies').find_one(req=None, _id=ID_FIELD_VALUE)

    def _find_keyword(self, keyword, keywords, property_to_match=VALUE):
        """
        Searches for keyword in keywords where keywords[index][property_to_match] == keyword.

        :param keyword: string to search
        :param keywords: list of dicts where each dict represents a keyword
        :param property_to_match: property name to be used for matching
        :return: None if not found. A dict having keyword properties if found.
        """

        for _keyword in keywords:
            if _keyword[property_to_match] == keyword:
                return _keyword

        return None

    def _copy_defaults(self, destination, source):
        """
        Copies the following properties - _created, _updated, _etag from source. Adds HATEOS to destination object.
        Since this resource is a mimic of a collection, the name is copied as _id in destination.
        """

        destination[config.ID_FIELD] = destination[NAME]
        destination[config.DATE_CREATED] = source[config.DATE_CREATED]
        destination[config.LAST_UPDATED] = source[config.LAST_UPDATED]
        destination[config.ETAG] = source[config.ETAG]
        build_custom_hateoas(_hateoas, destination)
