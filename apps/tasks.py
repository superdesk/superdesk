from superdesk.resource import Resource
from superdesk.notification import push_notification
from superdesk.utc import utcnow
from apps.archive.common import base_schema, on_create_item, item_url
from superdesk.services import BaseService
from eve.utils import ParsedRequest
import superdesk


def init_app(app):
    endpoint_name = 'tasks'
    service = TasksService(TaskResource.datasource['source'], backend=superdesk.get_backend())
    TaskResource(endpoint_name, app=app, service=service)


class TaskResource(Resource):
    datasource = {
        'source': 'archive',
        'default_sort': [('_updated', -1)],
        'filter': {'task': {'$exists': True}},
        'elastic_filter': {'exists': {'field': 'task'}}  # eve-elastic specific filter
    }
    item_url = item_url
    schema = {
        'slugline': base_schema['slugline'],
        'description_text': base_schema['description_text'],
        'type': base_schema['type'],
        'planning_item': Resource.rel('planning', True, type='string'),
        'task': {
            'type': 'dict',
            'schema': {
                'status': {
                    'type': 'string',
                    'allowed': ['todo', 'in-progress', 'done'],
                    'default': 'todo'
                },
                'due_date': {'type': 'datetime'},
                'started_at': {'type': 'datetime'},
                'finished_at': {'type': 'datetime'},
                'user': Resource.rel('users', True),
                'desk': Resource.rel('desks', True),
                'stage': Resource.rel('stages', True)
            }
        }
    }


class TasksService(BaseService):

    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        return self.backend.get('tasks', req=req, lookup=lookup)

    def update_times(self, doc):
        task = doc.get('task', {})
        status = task.get('status', None)
        if status == 'in-progress':
            task.setdefault('started_at', utcnow())

        if status == 'done':
            task.setdefault('finished_at', utcnow())

    def update_stage(self, doc):
        task = doc.get('task', {})
        desk_id = task.get('desk', None)
        stage_id = task.get('stage', None)
        if desk_id and not stage_id:
            desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)
            task['stage'] = desk['incoming_stage']

    def on_create(self, docs):
        on_create_item(docs)
        for doc in docs:
            self.update_times(doc)
            self.update_stage(doc)

    def on_update(self, updates, original):
        self.update_times(updates)

    def on_created(self, docs):
        push_notification(self.datasource, created=1)

    def on_updated(self, updates, original):
        push_notification(self.datasource, updated=1)

    def on_deleted(self, doc):
        push_notification(self.datasource, deleted=1)

    def assign_user(self, item_id, user):
        item = self.find_one(req=None, _id=item_id)
        item['task'] = item.get('task', {})
        item['task']['user'] = user
        del item['_id']
        return self.patch(item_id, item)
