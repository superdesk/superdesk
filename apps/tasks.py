from eve.utils import ParsedRequest

from superdesk.resource import Resource
from superdesk.notification import push_notification
from superdesk.utc import utcnow
from apps.archive.common import on_create_item, item_url
from superdesk.services import BaseService
from apps.content import metadata_schema
import superdesk
from superdesk.activity import add_activity, ACTIVITY_CREATE, ACTIVITY_UPDATE
from apps.archive.archive import get_subject
from copy import copy


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
        'slugline': metadata_schema['slugline'],
        'description_text': metadata_schema['description'],
        'type': metadata_schema['type'],
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
    privileges = {'POST': 'workflow', 'PATCH': 'workflow', 'DELETE': 'workflow'}


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

    def on_created(self, docs):
        push_notification(self.datasource, created=1)
        for doc in docs:
            if doc.get('task') and doc['task'].get('desk'):
                add_activity(ACTIVITY_CREATE, 'added new task {{ subject }} of type {{ type }}', item=doc,
                             subject=get_subject(doc), type=doc['type'])

    def on_update(self, updates, original):
        self.update_times(updates)

    def on_updated(self, updates, original):
        push_notification(self.datasource, updated=1)
        updated = copy(original)
        updated.update(updates)
        if updated.get('task') and updated['task'].get('desk'):
            add_activity(ACTIVITY_UPDATE, 'updated task {{ subject }} for item {{ type }}',
                         item=updated, subject=get_subject(updated))

    def on_deleted(self, doc):
        push_notification(self.datasource, deleted=1)

    def assign_user(self, item_id, user):
        item = self.find_one(req=None, _id=item_id)
        item['task'] = item.get('task', {})
        item['task']['user'] = user
        del item['_id']
        return self.patch(item_id, item)

superdesk.privilege(name='workflow',
                    label='Workflow Management',
                    description='User can change the state of an item within the workflow.')
