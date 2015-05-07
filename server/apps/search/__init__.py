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
from flask import current_app as app, json, g
from apps.archive.common import aggregations
from eve_elastic.elastic import set_filters


class SearchService(superdesk.Service):
    """Federated search service.

    It can search ingest/content/archive/spike at the same time.
    """

    available_repos = ('ingest', 'archive', 'text_archive', 'published')
    default_repos = ['ingest', 'archive', 'text_archive', 'published']

    private_filters = [{
        'or': [
            {'and': [{'exists': {'field': 'task.desk'}},
                     {'terms': {'state': ['fetched', 'routed', 'draft', 'in_progress', 'submitted']}}]},
            {'not': {'term': {'_type': 'archive'}}},
            {'and': [{'term': {'_type': 'published'}},
                     {'terms': {'state': ['published', 'killed']}}]}
        ]
    }]

    def get_private_filter(self):
        pass

    def _get_query(self, req):
        """Get elastic query."""
        args = getattr(req, 'args', {})
        query = json.loads(args.get('source')) if args.get('source') else {'query': {'filtered': {}}}
        query['aggs'] = aggregations
        return query

    def _get_types(self, req):
        """Get document types for the given query."""
        args = getattr(req, 'args', {})
        repos = args.get('repo', ','.join(self.default_repos)).split(',')
        return [repo for repo in repos if repo in self.available_repos]

    def get(self, req, lookup):
        """Run elastic search agains on multiple doc types."""
        elastic = app.data.elastic
        query = self._get_query(req)
        types = self._get_types(req)
        query['aggs'] = aggregations
        stages = superdesk.get_resource_service('users').get_invisible_stages_ids(g.get('user', {}).get('_id'))
        if stages:
            self.private_filters.append({'and': [{'not': {'terms': {'task.stage': stages}}}]})
        # if the system has a setting value for the maximum search depth then apply the filter
        if not app.settings['MAX_SEARCH_DEPTH'] == -1:
            set_filters(query, self.private_filters + [{'limit': {'value': app.settings['MAX_SEARCH_DEPTH']}}])
        else:
            set_filters(query, self.private_filters)
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
    search_service = SearchService('archive', backend=superdesk.get_backend())
    SearchResource('search', app=app, service=search_service)
