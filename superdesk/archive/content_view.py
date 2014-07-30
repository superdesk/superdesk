from eve.utils import ParsedRequest

import superdesk
from superdesk.base_model import BaseModel
from settings import URL_PREFIX
from flask import current_app as app
import flask


class ContentViewModel(BaseModel):
    endpoint_name = 'content_view'
    schema = {
        'name': {
            'type': 'string',
            'unique': True,
            'required': True,
            'minlength': 1
        },
        'description': {
            'type': 'string',
            'required': True,
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
        url = URL_PREFIX + '/' + location + '?source=' + filter
        payload = None
        with app.test_request_context(url, method='GET'):
            try:
                superdesk.apps[location].get(req=parsed_request, lookup={})
            except Exception as e:
                payload = 'Fail to validate the filter against %s. ' % location
                payload = payload + 'The search returns the following error: %s' % str(e)
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


location_content_view = {
    'current_desk': {
        'type': 'string'
    },
    'location': {
        'type': 'string',
        'allowed': ['ingest', 'archive'],
        'required': True
    }
}


class UserContentViewModel(BaseModel):
    endpoint_name = 'user_content_view'
    schema = location_content_view
    resource_methods = ['GET']

    def get(self, req, lookup):
        # TODO: change the condition for role when the user support multiple roles
        user = flask.g.user
        filter = {"$or": [{"roles": user['role']}, {"roles": None}]}
        if 'desk' in lookup and lookup['desk']:
            filter = {"$and": [filter, {"$or": [{"desks": lookup['desk']}, {"desks": None}]}]}
        return superdesk.apps[lookup['location']].get(req=None, lookup=filter)
