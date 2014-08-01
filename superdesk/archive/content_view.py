from eve.utils import ParsedRequest

import superdesk
from superdesk.base_model import BaseModel
import logging

logger = logging.getLogger(__name__)


class ContentViewModel(BaseModel):
    endpoint_name = 'content_view'
    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'minlength': 1
        },
        'description': {
            'type': 'string',
            'minlength': 1
        },
        'location': {
            'type': 'string',
            'allowed': ['ingest', 'archive'],
            'required': True
        },
        'desks': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        },
        'roles': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        },
        'filter': {
            'type': 'string'
        }
    }

    def check_filter(self, filter, location):
        # TOOD: change this after refactoring Eve to avoid direct access to request
        # object on datalayer
        parsed_request = ParsedRequest()
        parsed_request.args = {'source': filter}
        payload = None
        try:
            superdesk.apps[location].get(req=parsed_request, lookup={})
        except Exception as e:
            logger.exception(e)
            payload = 'Fail to validate the filter against %s.' % location
        if payload:
            raise superdesk.SuperdeskError(payload=payload)

    def process_and_validate(self, doc):
        # if desks/roles list is empty set it as None in order filter by desks/roles more easily
        if 'desks' in doc and not doc['desks']:
            del doc['desks']
        if 'roles' in doc and not doc['roles']:
            del doc['roles']

        if 'filter' in doc and doc['filter']:
            self.check_filter(doc['filter'], doc['location'])

    def on_create(self, docs):
        for doc in docs:
            self.process_and_validate(doc)

    def on_update(self, updates, original):
        self.process_and_validate(updates)
