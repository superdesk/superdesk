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
import re
from flask import request
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
            'nullable': False
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
    def create(self, docs, **kwargs):
        if request.args.get('article_id', None):
            for doc in docs:
                article_id = request.args.get('article_id')
                article = get_resource_service('archive').find_one(req=None, _id=article_id)
                if not article:
                    raise SuperdeskApiError.badRequestError('Article not found!')
                doc['matches'] = self.does_match(doc, article)
            return [doc['matches'] for doc in docs]
        self._validate_publish_filters(docs)
        return super().create(docs, **kwargs)

    def update(self, id, updates, original):
        publish_filter = dict(original)
        publish_filter.update(updates)
        self._validate_no_circular_reference(publish_filter, publish_filter['_id'])
        super().update(id, updates, original)

    def delete(self, lookup):
        referenced_filters = self._get_referenced_publish_filters(lookup.get('_id'))
        if referenced_filters.count() > 0:
            references = ','.join([pf['name'] for pf in referenced_filters])
            raise SuperdeskApiError.badRequestError('Publish filter has been referenced in {}'.format(references))
        return super().delete(lookup)

    def _validate_publish_filters(self, docs):
        for doc in docs:
            if not doc.get('name', None):
                raise SuperdeskApiError.badRequestError('Name cannot be empty')
            publish_filters = get_resource_service('publish_filters').\
                get(req=None, lookup={'name': {'$regex': re.compile('^{}$'.format(doc['name']), re.IGNORECASE)}})
            if publish_filters and publish_filters.count() > 0:
                raise SuperdeskApiError.badRequestError('Publish filter {} already exists'.format(doc['name']))

    def _get_referenced_publish_filters(self, id):
        lookup = {'publish_filter.expression.pf': [id]}
        publish_filters = get_resource_service('publish_filters').get(req=None, lookup=lookup)
        return publish_filters

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
        return {'query': {'filtered': {'query': {'bool': self._get_elastic_query(doc)}}}}

    def _get_elastic_query(self, doc):
        expressions = {'should': []}
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

            expressions['should'].append({'bool': filter_conditions})
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
