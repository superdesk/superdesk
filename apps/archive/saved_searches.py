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

from flask import request
from eve.utils import ParsedRequest
from eve_elastic.elastic import build_elastic_query

from superdesk import Resource, get_resource_service, SuperdeskError
from superdesk.services import BaseService


logger = logging.getLogger(__name__)


class SavedSearchesResource(Resource):
    endpoint_name = resource_title = 'saved_searches'
    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'minlength': 1
        },
        'filter': {
            'type': 'dict',
            'required': True
        },
        'user': Resource.rel('users'),
    }

    url = 'users/<regex("[a-zA-Z0-9:\\-\\.]+"):user>/saved_searches'

    item_methods = ['GET', 'DELETE']

    privileges = {'POST': 'saved_searches', 'DELETE': 'saved_searches'}


class SavedSearchesService(BaseService):
    def on_create(self, docs):
        for doc in docs:
            doc.setdefault('user', request.view_args['user'])
            self.__process_and_validate(doc)

    def get(self, req, lookup):
        """
        Overriding because of a different resource URL and user_id is part of the URL
        """

        req = ParsedRequest()
        req.where = json.dumps(lookup)
        return super().get(req, lookup=None)

    def init_request(self, elastic_query):
        """
        Initializes request object.
        """

        parsed_request = ParsedRequest()
        parsed_request.args = {"source": json.dumps(elastic_query)}

        return parsed_request

    def get_location(self, doc):
        """
        Returns location from the doc object and deletes it so that it's not passed to elastic query
        :param doc:
        :return: location
        """

        return doc['filter']['query'].get('repo', 'archive')

    def __process_and_validate(self, doc):
        """
        Processes the Saved Search document and validates the saved search against ElasticSearch
        """

        if not doc['filter'].get('query'):
            raise SuperdeskError(message='Fail to validate the filter.', status_code=400)

        location, elastic_query = self.get_location(doc), build_elastic_query(
            {k: v for k, v in doc['filter']['query'].items() if k != 'repo'})

        self.__validate_elastic_query(elastic_query, location)

    def __validate_elastic_query(self, elastic_query, index):
        """
        Validates the elastic_query against ElasticSearch.

        :param elastic_query: JSON format inline with ElasticSearch syntax
        :param index: Name of the ElasticSearch index
        :raise SuperdeskError: If failed to validate the elastic_query against ElasticSearch
        """

        parsed_request = self.init_request(elastic_query)
        try:
            get_resource_service(index).get(req=parsed_request, lookup={})
        except Exception as e:
            logger.exception(e)
            raise SuperdeskError(message='Fail to validate the filter against %s.' % index, status_code=400)


class SavedSearchItemsResource(Resource):
    """
    Since Eve doesn't support more than one URL for a resource, this resource is being created to fetch items based on
    the search string in the Saved Search document.
    """

    endpoint_name = 'saved_search_items'
    schema = SavedSearchesResource.schema

    resource_title = endpoint_name
    url = 'saved_searches/<regex("[a-zA-Z0-9:\\-\\.]+"):saved_search_id>/items'

    resource_methods = ['GET']
    item_methods = []


class SavedSearchItemsService(SavedSearchesService):
    def get(self, req, **lookup):
        saved_search_id = lookup['lookup']['saved_search_id']
        saved_search = get_resource_service('saved_searches').find_one(req=None, _id=saved_search_id)

        if not saved_search:
            raise SuperdeskError(message="Invalid Saved Search", status_code=404)

        return self.__process_and_fetch_documents(saved_search)

    def __process_and_fetch_documents(self, doc):
        """
        Processes the Saved Search document and fetches documents from ElasticSearch

        :param doc: Saved Search document
        :raise SuperdeskError: If failed to validate the elastic_query against ElasticSearch
        """

        if not doc['filter'].get('query'):
            raise SuperdeskError(message='Fail to validate the filter.', status_code=400)

        location, elastic_query = self.get_location(doc), build_elastic_query(
            {k: v for k, v in doc['filter']['query'].items() if k != 'repo'})

        parsed_request = self.init_request(elastic_query)

        try:
            return get_resource_service(location).get(req=parsed_request, lookup={})
        except Exception as e:
            logger.exception(e)
            raise SuperdeskError(message='Fail to validate the filter against %s.' % location, status_code=400)
