from superdesk.notification import push_notification
from superdesk.base_model import BaseModel
from superdesk.archive.common import on_create_item


def init_app(app):
    PlanningModel(app=app)


class PlanningModel(BaseModel):
    endpoint_name = 'planning'
    schema = {
        'guid': {
            'type': 'string',
            'unique': True
        },
        'language': {
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
        'desk': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'desks',
                'field': '_id',
                'embeddable': True
            }
        }
    }
    item_url = 'regex("[\w,.:-]+")'
    datasource = {
        'backend': 'elastic'
    }
    resource_methods = ['GET', 'POST']

    def on_create(self, docs):
        on_create_item(docs)
        push_notification('planning', created=1)

    def on_update(self, updates, original):
        push_notification('planning', updated=1)

    def on_delete(self, doc):
        push_notification('planning', deleted=1)
