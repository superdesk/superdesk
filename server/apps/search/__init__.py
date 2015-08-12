# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import current_app as app, json, g
from eve_elastic.elastic import set_filters

import superdesk
from apps.archive.common import aggregations
from superdesk.metadata.item import CONTENT_STATE, ITEM_STATE
from apps.archive.archive import SOURCE as ARCHIVE


class SearchService(superdesk.Service):
    """
    Federated search service.

    It can search against different collections like Ingest, Production, Archived etc.. at the same time.
    """

    def __init__(self, datasource, backend):
        super().__init__(datasource=datasource, backend=backend)
        self._default_repos = ['ingest', 'archive', 'published', 'archived']

        self._private_filters = [{
            'or': [
                {'and': [{'term': {'_type': 'ingest'}}]},
                {'and': [{'exists': {'field': 'task.desk'}},
                         {'terms': {ITEM_STATE: [CONTENT_STATE.FETCHED, CONTENT_STATE.ROUTED, CONTENT_STATE.DRAFT,
                                                 CONTENT_STATE.PROGRESS, CONTENT_STATE.SUBMITTED]}}]},
                {'and': [{'term': {'_type': 'published'}},
                         {'term': {'allow_post_publish_actions': True}},
                         {'terms': {ITEM_STATE: [CONTENT_STATE.SCHEDULED, CONTENT_STATE.PUBLISHED, CONTENT_STATE.KILLED,
                                                 CONTENT_STATE.CORRECTED]}}]},
                {'and': [{'term': {'_type': 'published'}},
                         {'term': {'allow_post_publish_actions': False}},
                         {'term': {'can_be_removed': False}}]}
            ]
        }]

    def _get_query(self, req):
        """Get elastic query."""
        args = getattr(req, 'args', {})
        query = json.loads(args.get('source')) if args.get('source') else {'query': {'filtered': {}}}
        query['aggs'] = aggregations
        return query

    def _get_types(self, req):
        """Get document types for the given query."""
        args = getattr(req, 'args', {})
        repos = args.get('repo')

        if repos is None:
            return self._default_repos
        else:
            repos = repos.split(',')
            return [repo for repo in repos if repo in self._default_repos]

    def get(self, req, lookup):
        """
        Runs elastic search on multiple doc types.
        """

        elastic = app.data.elastic
        query = self._get_query(req)
        types = self._get_types(req)
        query['aggs'] = aggregations

        stages = superdesk.get_resource_service('users').get_invisible_stages_ids(g.get('user', {}).get('_id'))
        if stages:
            self._private_filters.append({'and': [{'not': {'terms': {'task.stage': stages}}}]})

        # if the system has a setting value for the maximum search depth then apply the filter
        if not app.settings['MAX_SEARCH_DEPTH'] == -1:
            set_filters(query, self._private_filters + [{'limit': {'value': app.settings['MAX_SEARCH_DEPTH']}}])
        else:
            set_filters(query, self._private_filters)

        hits = elastic.es.search(body=query, index=elastic.index, doc_type=types)
        docs = elastic._parse_hits(hits, 'ingest')  # any resource here will do

        for resource in types:
            response = {app.config['ITEMS']: [doc for doc in docs if doc['_type'] == resource]}
            getattr(app, 'on_fetched_resource')(resource, response)
            getattr(app, 'on_fetched_resource_%s' % resource)(response)

        return docs


class SearchResource(superdesk.Resource):
    resource_methods = ['GET']
    item_methods = []


def init_app(app):
    search_service = SearchService(ARCHIVE, backend=superdesk.get_backend())
    SearchResource('search', app=app, service=search_service)
