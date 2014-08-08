from eve.utils import ParsedRequest

import superdesk
import json
from superdesk.base_model import BaseModel
import logging
import flask
from eve.methods.common import build_response_document

logger = logging.getLogger(__name__)


def get_elastic_filter(filter):
    parsed_request = ParsedRequest()
    parsed_request.args = {'source': json.dumps({'query': {'filtered': {'filter': filter}}})}
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
        },
        'items': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'content_view_items',
                'field': '_id',
                'embeddable': True
            }
        }
    }

    def check_filter(self, filter, location):
        parsed_request = get_elastic_filter(filter)
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
            filter_doc = {'filter': doc['filter'], 'location': doc['location']}
            doc['items'] = superdesk.apps['content_view_items'].create([filter_doc])[0]

    def on_create(self, docs):
        for doc in docs:
            doc.setdefault('user', flask.g.user.get('_id'))
            self.process_and_validate(doc)

    def on_update(self, updates, original):
        self.process_and_validate(updates)


class ContentViewItemsModel(BaseModel):
    endpoint_name = 'content_view_items'
    internal_resource = True
    schema = {
        'location': {
            'type': 'string',
            'allowed': ['ingest', 'archive'],
            'default': 'archive'
        },
        'filter': {
            'type': 'dict'
        },
        'view_items': {'type': 'list'}
    }

    def find_one(self, req, **lookup):
        view_items = super().find_one(req=req, **lookup)
        parsed_request = get_elastic_filter(view_items['filter'])
        location = view_items['location']
        cursor = superdesk.apps[location].get(req=parsed_request, lookup={})
        documents = []
        for document in cursor:
            build_response_document(document, location, [])
            documents.append(document)
        view_items['view_items'] = documents
        return view_items
