from superdesk.base_model import BaseModel
from superdesk.notification import push_notification


def init_app(app):
    TaskModel(app=app)


def rel(resource, embeddable=False, required=False):
    return {
        'type': 'objectid',
        'required': required,
        'data_relation': {'resource': resource, 'field': '_id', 'embeddable': embeddable}
    }


class TaskModel(BaseModel):
    endpoint_name = 'tasks'
    schema = {
        'title': {
            'type': 'string',
            'required': True
        },
        'description': {'type': 'string'},
        'type': {
            'type': 'string',
            'allowed': ['story', 'photo', 'video', 'graphics', 'live-blogging'],
            'default': 'story',
            'required': True
        },
        'status': {
            'type': 'string',
            'allowed': ['todo', 'in-progress', 'done'],
            'default': 'todo',
            'required': True
        },
        'due_date': {'type': 'datetime'},
        'assigned_user': rel('users', True, True),
        'assigned_desk': rel('desks', True),
        'planning_item': {'type': 'string'},
    }

    def on_created(self, docs):
        push_notification(self.endpoint_name, created=1)

    def on_updated(self, updates, original):
        push_notification(self.endpoint_name, updated=1)

    def on_deleted(self, doc):
        push_notification(self.endpoint_name, deleted=1)
