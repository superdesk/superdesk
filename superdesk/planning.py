from superdesk.notification import push_notification
from superdesk.base_model import BaseModel
from superdesk.items import on_create_item


planning_schema = {
    'guid': {
        'type': 'string',
        'unique': True
    },
    'type': {
        'type': 'string',
        'required': True
    },
    'version': {
        'type': 'string'
    },
    'versioncreated': {
        'type': 'datetime'
    },
    'language': {
        'type': 'string'
    },
    'byline': {
        'type': 'string'
    },
    'creditline': {
        'type': 'string'
    },
    'headline': {
        'type': 'string'
    },
    'slugline': {
        'type': 'string'
    },
    'description_text': {
        'type': 'string',
        'nullable': True
    },
    'firstcreated': {
        'type': 'datetime'
    },
    'urgency': {
        'type': 'integer'
    },
    'edNote': {
        'type': 'string'
    },
    'scheduled': {
        'type': 'datetime'
    },
    'desk': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'desks',
            'field': '_id',
            'embeddable': True
        }
    },
}

item_url = 'regex("[\w,.:-]+")'

extra_response_fields = ['guid', 'headline', 'firstcreated', 'versioncreated']

facets = {
    'type': {'terms': {'field': 'type'}},
    'urgency': {'terms': {'field': 'urgency'}},
    'subject': {'terms': {'field': 'subject.name'}},
    'versioncreated': {'date_histogram': {'field': 'versioncreated', 'interval': 'hour'}},
}


def on_create_planning():
    push_notification('planning', created=1)


def on_update_planning():
    push_notification('planning', updated=1)


def on_delete_planning():
    push_notification('planning', deleted=1)


def init_app(app):
    PlanningModel(app=app)


class PlanningModel(BaseModel):
    endpoint_name = 'planning'
    schema = planning_schema
    extra_response_fields = extra_response_fields
    item_url = item_url
    datasource = {
        'backend': 'elastic',
        'facets': facets
    }
    resource_methods = ['GET', 'POST']

    def on_create(self, docs):
        on_create_item(docs)
        on_create_planning()

    def on_update(self, updates, original):
        on_update_planning()

    def on_delete(self, doc):
        on_delete_planning()
