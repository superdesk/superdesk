import json
import logging

from eve.utils import ParsedRequest

import superdesk
from superdesk.archive.common import base_schema, get_user
from superdesk.base_model import BaseModel, build_custom_hateoas
from superdesk.json_path_tool import json_merge_values, json_copy_values


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
        'desk': BaseModel.rel('desks', True),
        'user': BaseModel.rel('users', True),
        'filter': {
            'type': 'dict'
        },
        'hateoas': {
            'self': '/{location}/{_id}'
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


def merge_query(first, second):
    return {"bool": {"should": [first, second], "minimum_should_match": 2}}


def merge_filter(first, second):
    return {'and': [first, second]}


def apply_additional_query(query, additional_query):
    if not query:
        query = additional_query
    elif additional_query:
        json_merge_values(query, additional_query, ['query', 'filtered', 'query'], merge_query)
        json_merge_values(query, additional_query, ['query', 'filtered', 'filter'], merge_filter)
        json_copy_values(query, additional_query, ['size', 'from', 'sort'])

    return query


class ContentViewItemsModel(BaseModel):
    endpoint_name = 'content_view_items'
    resource_title = endpoint_name
    url = 'content_view/<regex("[a-zA-Z0-9:\\-\\.]+"):content_view_id>/items'
    schema = base_schema
    resource_methods = ['GET']
    datasource = {'backend': 'custom'}
    custom_hateoas = {'self': {'title': 'Archive', 'href': '/{location}/{_id}'}}

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
        location = view_items.get('location', 'archive')
        docs = superdesk.apps[location].get(req=parsed_request, lookup={})

        for doc in docs:
            build_custom_hateoas(self.custom_hateoas, doc, location=location)
        return docs
