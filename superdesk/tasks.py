from superdesk.base_model import BaseModel
from superdesk.notification import push_notification
from superdesk.utc import utcnow


def init_app(app):
    TaskModel(app=app)


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
        'started_at': {'type': 'datetime'},
        'finished_at': {'type': 'datetime'},
        'assigned_user': BaseModel.rel('users', True, True),
        'assigned_desk': BaseModel.rel('desks', True),
        'planning_item': BaseModel.rel('planning', True, type='string')
    }

    def update_times(self, doc):
        status = doc.get('status', None)
        if status == 'in-progress':
            doc.setdefault('started_at', utcnow())

        if status == 'done':
            doc.setdefault('finished_at', utcnow())

    def on_create(self, docs):
        for doc in docs:
            self.update_times(doc)

    def on_update(self, updates, original):
        self.update_times(updates)

    def on_created(self, docs):
        push_notification(self.endpoint_name, created=1)

    def on_updated(self, updates, original):
        push_notification(self.endpoint_name, updated=1)

    def on_deleted(self, doc):
        push_notification(self.endpoint_name, deleted=1)
