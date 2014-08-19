import json
import logging

from eve.utils import ParsedRequest

import superdesk
from superdesk.archive.common import base_schema, get_user
from superdesk.base_model import BaseModel


logger = logging.getLogger(__name__)


def init_parsed_request(filter):
    parsed_request = ParsedRequest()
    if filter:
        parsed_request.args = {'source': json.dumps(filter)}
    return parsed_request


class ContentViewModel(BaseModel):
    endpoint_name = 'content_view'
    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'minlength': 1
        },
        'location': {
            'type': 'string',
            'allowed': ['ingest', 'archive'],
            'default': 'archive'
        },
        'description': {
            'type': 'string',
            'minlength': 1
        },
        'desk': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'desks',
                'field': '_id',
                'embeddable': True
            }
        },
        'user': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'users',
                'field': '_id',
                'embeddable': True
            }
        },
        'filter': {
            'type': 'dict'
        }
    }

    def check_filter(self, filter, location):
        parsed_request = init_parsed_request(filter)
        payload = None
        try:
            superdesk.apps[location].get(req=parsed_request, lookup={})
        except Exception as e:
            logger.exception(e)
            payload = 'Fail to validate the filter against %s.' % location
        if payload:
            raise superdesk.SuperdeskError(payload=payload)

    def process_and_validate(self, doc):
        if 'desks' in doc and not doc['desks']:
            del doc['desks']

        if 'filter' in doc and doc['filter']:
            self.check_filter(doc['filter'], doc['location'])

    def on_create(self, docs):
        for doc in docs:
            doc.setdefault('user', get_user(required=True)['_id'])
            self.process_and_validate(doc)

    def on_update(self, updates, original):
        self.process_and_validate(updates)


def json_get(json, path):
    crt = json
    for name in path:
        if name in crt:
            crt = crt[name]
        else:
            return None
    return crt


def json_set(json, path, value):
    crt = json
    for name in path[:-1]:
        if name not in crt:
            crt[name] = {}
        crt = crt[name]
    crt[path[-1]] = value


def combine_query(first, second):
    return '(' + first + ') AND (' + second + ')'


def combine_filter(first, second):
    return {'and': [first, second]}


def update_query(query, additional_query, path, combine):
    term = json_get(query, path)
    aditional_term = json_get(additional_query, path)

    if not aditional_term:
        return

    if term:
        json_set(query, path, combine(term, aditional_term))
    else:
        json_set(query, path, aditional_term)


def update_query_defaults(query, additional_query):
    attributes = ['size', 'from', 'sort']
    for attribute in attributes:
        if attribute not in query and attribute in additional_query:
            query[attribute] = additional_query[attribute]


def apply_additional_query(query, additional_query):
    if not query:
        query = additional_query
    elif additional_query:
        update_query(query, additional_query, ['query', 'filtered', 'query', 'query_string', 'query'], combine_query)
        update_query(query, additional_query, ['query', 'filtered', 'filter'], combine_filter)
        update_query_defaults(query, additional_query)

    return query


class ContentViewItemsModel(BaseModel):
    endpoint_name = 'content_view_items'
    url = 'content_view/<regex("[a-zA-Z0-9:\\-\\.]+"):content_view_id>/items'
    schema = base_schema
    resource_methods = ['GET']
    datasource = {'backend': 'custom'}

    def get(self, req, **lookup):
        content_view_id = lookup['lookup']['content_view_id']
        view_items = superdesk.apps['content_view'].find_one(req=None, _id=content_view_id)
        if not view_items:
            raise superdesk.SuperdeskError(payload='Invalid content view id.')
        additional_query = view_items.get('filter')

        query = None
        if req.args.get('source'):
            query = json.loads(req.args.get('source'))

        query = apply_additional_query(query, additional_query)
        parsed_request = init_parsed_request(query)
        location = view_items['location']

        return superdesk.apps[location].get(req=parsed_request, lookup={})
