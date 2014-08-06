from eve.utils import ParsedRequest

import superdesk
import json
from superdesk.base_model import BaseModel
import logging
from flask import current_app as app
import flask

logger = logging.getLogger(__name__)


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
        parsed_request = ParsedRequest()
        parsed_request.args = {'source': json.dumps({'query': {'filtered': {'filter': filter}}})}
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
        user = getattr(flask.g, 'user') if hasattr(flask.g, 'user') else {}
        if not user:
            if app.debug:
                user = {}
            else:
                raise superdesk.SuperdeskError(payload='Invalid user.')

        for doc in docs:
            doc.setdefault('user', user)
            self.process_and_validate(doc)

    def on_update(self, updates, original):
        self.process_and_validate(updates)
