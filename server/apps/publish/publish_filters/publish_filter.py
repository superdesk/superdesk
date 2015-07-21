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


class PublishFilterResource(Resource):
    schema = {
        'publish_filter': {
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
                                'schema': Resource.rel('publish_filters', True)
                            }
                        }
                    }
                }
            }
        },
        'name': {
            'type': 'string',
            'nullable': False,
            'iunique': True
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

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'publish_filters',
                  'PATCH': 'publish_filters',
                  'DELETE': 'publish_filters'}


class PublishFilterService(BaseService):
    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        if req.args and req.args.get('is_global'):
            lookup = {'is_global': True}
        return self.backend.get(self.datasource, req=req, lookup=lookup)

    def update(self, id, updates, original):
        publish_filter = dict(original)
        publish_filter.update(updates)
        self._validate_no_circular_reference(publish_filter, publish_filter['_id'])
        super().update(id, updates, original)

    def delete(self, lookup):
        referenced_filters = self._get_publish_filters_by_publish_filter(lookup.get('_id'))
        if referenced_filters.count() > 0:
            references = ','.join([pf['name'] for pf in referenced_filters])
            raise SuperdeskApiError.badRequestError('Publish filter has been referenced in {}'.format(references))
        return super().delete(lookup)

    def _get_publish_filters_by_publish_filter(self, publish_filter_id):
        lookup = {'publish_filter.expression.pf': {'$in': [publish_filter_id]}}
        publish_filters = get_resource_service('publish_filters').get(req=None, lookup=lookup)
        return publish_filters

    def _get_publish_filters_by_filter_condition(self, filter_condition_id):
        lookup = {'publish_filter.expression.fc': {'$in': [filter_condition_id]}}
        publish_filters = super().get(req=None, lookup=lookup)
        all_publish_filters = self._get_referenced_publish_filters(list(publish_filters), None)
        return all_publish_filters

    def _get_referenced_publish_filters(self, publish_filters, pf_list):
        if not pf_list:
            pf_list = []

        for pf in publish_filters:
            pf_list.append(pf)
            references = list(self._get_publish_filters_by_publish_filter(pf['_id']))
            if references and len(references) > 0:
                return self._get_referenced_publish_filters(references, pf_list)
        return pf_list

    def _validate_no_circular_reference(self, publish_filter, filter_id):
        for expression in publish_filter.get('publish_filter', []):
            if 'pf' in expression.get('expression', {}):
                for f in expression['expression']['pf']:
                    current_filter = super().find_one(req=None, _id=f)
                    if f == filter_id:
                        raise SuperdeskApiError.badRequestError('Circular dependency error in publish filters:{}'
                                                                .format(current_filter['name']))
                    self._validate_no_circular_reference(current_filter, filter_id)

    def build_mongo_query(self, doc):
        filter_condition_service = get_resource_service('filter_conditions')
        expressions = []
        for expression in doc.get('publish_filter', []):
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
        for expression in doc.get('publish_filter', []):
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

    def does_match(self, publish_filter, article):
        filter_condition_service = get_resource_service('filter_conditions')
        expressions = []
        for expression in publish_filter.get('publish_filter', []):
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


class PublishFilterTestResource(Resource):
    item_url = 'regex("[\w,.:_-]+")'
    endpoint_name = 'publish_filter_tests'
    schema = {
        'filter_id': {'type': 'string'},
        'article_id': {'type': 'string'},
        'return_matching': {'type': 'boolean'},
        'filter': {'type': 'dict'}
    }
    url = 'publish_filters/test'.format(item_url)
    resource_methods = ['POST']
    resource_title = endpoint_name
    privileges = {'POST': 'publish_filters'}


class PublishFilterTestService(BaseService):

    def create(self, docs, **kwargs):
        service = get_resource_service('publish_filters')
        for doc in docs:
            filter_id = doc.get('filter_id')
            if filter_id:
                publish_filter = service.find_one(req=None, _id=filter_id)
            else:
                publish_filter = doc.get('filter')

            if not publish_filter:
                    raise SuperdeskApiError.badRequestError('Publish filter not found')

            if 'article_id' in doc:
                article_id = doc.get('article_id')
                article = get_resource_service('archive').find_one(req=None, _id=article_id)
                if not article:
                    raise SuperdeskApiError.badRequestError('Article not found!')
                try:
                    doc['match_results'] = service.does_match(publish_filter, article)
                except Exception as ex:
                    raise SuperdeskApiError.\
                        badRequestError('Error in testing article: {}'.format(str(ex)))
            else:
                try:
                    if doc.get('return_matching', True):
                        query = service.build_elastic_query(publish_filter)
                    else:
                        query = service.build_elastic_not_filter(publish_filter)
                    req = ParsedRequest()
                    req.args = {'source': json.dumps(query)}
                    doc['match_results'] = list(get_resource_service('archive').get(req=req, lookup=None))
                except Exception as ex:
                    raise SuperdeskApiError.\
                        badRequestError('Error in testing archive: {}'.format(str(ex)))

        return [doc['match_results'] for doc in docs]
