from superdesk.models import BaseModel
from superdesk.notification import push_notification
from superdesk.utc import utcnow
from apps.archive.common import base_schema


def init_app(app):
    TaskModel(app=app)


class TaskModel(BaseModel):
    endpoint_name = 'tasks'
    datasource = {
        'source': 'archive',
        'default_sort': [('_updated', -1)],
        'filter': {'task': {'$exists': True}},
        'elastic_filter': {'exists': {'field': 'task'}}  # eve-elastic specific filter
    }
    schema = {
        'slugline': base_schema['slugline'],
        'description_text': base_schema['description_text'],
        'type': base_schema['type'],
        'planning_item': BaseModel.rel('planning', True, type='string'),
        'task': {
            'type': 'dict',
            'schema': {
                'status': {
                    'type': 'string',
                    'allowed': ['todo', 'in-progress', 'done'],
                    'default': 'todo',
                    'required': True
                },
                'due_date': {'type': 'datetime'},
                'started_at': {'type': 'datetime'},
                'finished_at': {'type': 'datetime'},
                'user': BaseModel.rel('users', True),
                'desk': BaseModel.rel('desks', True),
                'basket': BaseModel.rel('content_view', True)
            }
        }
    }

    def update_times(self, doc):
        task = doc.get('task', {})
        status = task.get('status', None)
        if status == 'in-progress':
            task.setdefault('started_at', utcnow())

        if status == 'done':
            task.setdefault('finished_at', utcnow())

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
