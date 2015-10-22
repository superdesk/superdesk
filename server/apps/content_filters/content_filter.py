# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
import json
from eve.utils import ParsedRequest
from superdesk import get_resource_service
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError


logger = logging.getLogger(__name__)


class ContentFilterResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'nullable': False,
            'empty': False,
            'iunique': True
        },
        'content_filter': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'expression': {
                        'type': 'dict',
                        'schema': {
                            'fc': {
                                'type': 'list',
                                'schema': Resource.rel('filter_conditions', True)
                            },
                            'pf': {
                                'type': 'list',
                                'schema': Resource.rel('content_filters', True)
                            }
                        }
                    }
                }
            }
        },
        'is_global': {
            'type': 'boolean',
            'default': False
        }
    }

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'name'
    }

    privileges = {'POST': 'content_filters',
                  'PATCH': 'content_filters',
                  'DELETE': 'content_filters'}


class ContentFilterService(BaseService):
    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        if req.args and req.args.get('is_global'):
            lookup = {'is_global': True}
        return self.backend.get(self.datasource, req=req, lookup=lookup)

    def update(self, id, updates, original):
        content_filter = dict(original)
        content_filter.update(updates)
        self._validate_no_circular_reference(content_filter, content_filter['_id'])
        super().update(id, updates, original)

    def delete(self, lookup):
        filter_id = lookup.get('_id')

        # check if the filter is referenced by any subscribers...
        subscribers = self._get_referencing_subscribers(filter_id)
        if subscribers.count() > 0:
            references = ','.join(s['name'] for s in subscribers)
            raise SuperdeskApiError.badRequestError(
                'Content filter has been referenced by '
                'subscriber(s) {}'.format(references)
            )

        # check if the filter is referenced by any routing schemes...
        schemes = self._get_referencing_routing_schemes(filter_id)
        if schemes.count() > 0:
            references = ','.join(s['name'] for s in schemes)
            raise SuperdeskApiError.badRequestError(
                'Content filter has been referenced by '
                'routing scheme(s) {}'.format(references)
            )

        # check if the filter is referenced by any other content filters...
        referenced_filters = self._get_content_filters_by_content_filter(filter_id)
        if referenced_filters.count() > 0:
            references = ','.join([pf['name'] for pf in referenced_filters])
            raise SuperdeskApiError.badRequestError(
                'Content filter has been referenced in {}'.format(references))

        return super().delete(lookup)

    def _get_content_filters_by_content_filter(self, content_filter_id):
        lookup = {'content_filter.expression.pf': {'$in': [content_filter_id]}}
        content_filters = get_resource_service('content_filters').get(req=None, lookup=lookup)
        return content_filters

    def _get_referencing_subscribers(self, filter_id):
        """Fetch all subscribers from database that contain a reference to the
        given filter.

        :param str filter_id: the referenced filter's ID

        :return: DB cursor over the results
        :rtype: :py:class:`pymongo.cursor.Cursor`
        """
        subscribers_service = get_resource_service('subscribers')
        subscribers = subscribers_service.get(
            req=None,
            lookup={'content_filter.filter_id': filter_id})
        return subscribers

    def _get_referencing_routing_schemes(self, filter_id):
        """Fetch all routing schemes from database that contain a reference to
        the given filter.

        :param str filter_id: the referenced filter's ID

        :return: DB cursor over the results
        :rtype: :py:class:`pymongo.cursor.Cursor`
        """
        routing_schemes_service = get_resource_service('routing_schemes')
        schemes = routing_schemes_service.get(
            req=None,
            lookup={'rules.filter': filter_id})
        return schemes

    def get_content_filters_by_filter_condition(self, filter_condition_id):
        lookup = {'content_filter.expression.fc': {'$in': [filter_condition_id]}}
        content_filters = super().get(req=None, lookup=lookup)
        all_content_filters = self._get_referenced_content_filters(
            list(content_filters), None)
        return all_content_filters

    def _get_referenced_content_filters(self, content_filters, pf_list):
        if not pf_list:
            pf_list = []

        for pf in content_filters:
            pf_list.append(pf)
            references = list(self._get_content_filters_by_content_filter(pf['_id']))
            if references and len(references) > 0:
                return self._get_referenced_content_filters(references, pf_list)
        return pf_list

    def _validate_no_circular_reference(self, content_filter, filter_id):
        for expression in content_filter.get('content_filter', []):
            if 'pf' in expression.get('expression', {}):
                for f in expression['expression']['pf']:
                    current_filter = super().find_one(req=None, _id=f)
                    if f == filter_id:
                        raise SuperdeskApiError.badRequestError(
                            'Circular dependency error in content filters:{}'
                            .format(current_filter['name'])
                        )
                    self._validate_no_circular_reference(current_filter, filter_id)

    def build_mongo_query(self, doc):
        filter_condition_service = get_resource_service('filter_conditions')
        expressions = []
        for expression in doc.get('content_filter', []):
            filter_conditions = []
            if 'fc' in expression.get('expression', {}):
                for f in expression['expression']['fc']:
                    current_filter = filter_condition_service.find_one(req=None, _id=f)
                    mongo_query = filter_condition_service.get_mongo_query(current_filter)
                    filter_conditions.append(mongo_query)
            if 'pf' in expression.get('expression', {}):
                for f in expression['expression']['pf']:
                    current_filter = super().find_one(req=None, _id=f)
                    mongo_query = self.build_mongo_query(current_filter)
                    filter_conditions.append(mongo_query)

            if len(filter_conditions) > 1:
                expressions.append({'$and': filter_conditions})
            else:
                expressions.extend(filter_conditions)

        if len(expressions) > 1:
            return {'$or': expressions}
        else:
            return expressions[0]

    def build_elastic_query(self, doc):
        return {'query': {'filtered': {'query': self._get_elastic_query(doc)}}}

    def build_elastic_not_filter(self, doc):
        return {'query': {'filtered': {'query': self._get_elastic_query(doc, matching=False)}}}

    def _get_elastic_query(self, doc, matching=True):
        expressions_list = []
        if matching:
            expressions = {'should': expressions_list}
        else:
            expressions = {'must_not': expressions_list}

        filter_condition_service = get_resource_service('filter_conditions')
        for expression in doc.get('content_filter', []):
            filter_conditions = {'must': []}
            if 'fc' in expression.get('expression', {}):
                for f in expression['expression']['fc']:
                    current_filter = filter_condition_service.find_one(req=None, _id=f)
                    elastic_query = filter_condition_service.get_elastic_query(current_filter)
                    filter_conditions['must'].append(elastic_query)
            if 'pf' in expression.get('expression', {}):
                for f in expression['expression']['pf']:
                    current_filter = super().find_one(req=None, _id=f)
                    elastic_query = self._get_elastic_query(current_filter)
                    filter_conditions['must'].append(elastic_query)

            expressions_list.append({'bool': filter_conditions})
        return {'bool': expressions}

    def does_match(self, content_filter, article):
        if not content_filter:
            return False  # a non-existing filter does not match anything

        filter_condition_service = get_resource_service('filter_conditions')
        expressions = []
        for expression in content_filter.get('content_filter', []):
            filter_conditions = []
            if 'fc' in expression.get('expression', {}):
                for f in expression['expression']['fc']:
                    filter_condition = filter_condition_service.find_one(req=None, _id=f)
                    filter_conditions.append(filter_condition_service.does_match(filter_condition, article))
            if 'pf' in expression.get('expression', {}):
                for f in expression['expression']['pf']:
                    current_filter = super().find_one(req=None, _id=f)
                    filter_conditions.append(self.does_match(current_filter, article))

            expressions.append(all(filter_conditions))
        return any(expressions)


class ContentFilterTestResource(Resource):
    item_url = 'regex("[\w,.:_-]+")'
    endpoint_name = 'content_filter_tests'
    schema = {
        'filter_id': {'type': 'string'},
        'article_id': {'type': 'string'},
        'return_matching': {'type': 'boolean'},
        'filter': {'type': 'dict'}
    }
    url = 'content_filters/test'.format(item_url)
    resource_methods = ['POST']
    resource_title = endpoint_name
    privileges = {'POST': 'content_filters'}


class ContentFilterTestService(BaseService):

    def create(self, docs, **kwargs):
        service = get_resource_service('content_filters')
        for doc in docs:
            filter_id = doc.get('filter_id')
            if filter_id:
                content_filter = service.find_one(req=None, _id=filter_id)
            else:
                content_filter = doc.get('filter')

            if not content_filter:
                    raise SuperdeskApiError.badRequestError('Content filter not found')

            if 'article_id' in doc:
                article_id = doc.get('article_id')
                article = get_resource_service('archive').find_one(req=None, _id=article_id)
                if not article:
                    raise SuperdeskApiError.badRequestError('Article not found!')
                try:
                    doc['match_results'] = service.does_match(content_filter, article)
                except Exception as ex:
                    raise SuperdeskApiError.\
                        badRequestError('Error in testing article: {}'.format(str(ex)))
            else:
                try:
                    if doc.get('return_matching', True):
                        query = service.build_elastic_query(content_filter)
                    else:
                        query = service.build_elastic_not_filter(content_filter)
                    req = ParsedRequest()
                    req.args = {'source': json.dumps(query)}
                    doc['match_results'] = list(get_resource_service('archive').get(req=req, lookup=None))
                except Exception as ex:
                    raise SuperdeskApiError.\
                        badRequestError('Error in testing archive: {}'.format(str(ex)))

        return [doc['match_results'] for doc in docs]
