import logging
from superdesk.resource import Resource, build_custom_hateoas
from superdesk.services import BaseService
from .tasks import TaskResource
import superdesk


logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'stages'
    service = StagesService(endpoint_name, backend=superdesk.get_backend())
    StagesResource(endpoint_name, app=app, service=service)
    endpoint_name = 'tasks_stage_items'
    service = TasksStageItemsService(TaskResource.datasource['source'], backend=superdesk.get_backend())
    TasksStageItemsResource(endpoint_name, app=app, service=service)


class StagesResource(Resource):
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
        'default_incoming': {
            'type': 'boolean',
            'required': True,
            'default': False
        },
        'desk': Resource.rel('desks', embeddable=True),
        'outgoing': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'stage': Resource.rel('stages', True)
                }
            }
        }
    }


class StagesService(BaseService):

    def on_delete(self, doc):
        if doc['default_incoming'] is True:
            desk_id = doc.get('desk', None)
            if desk_id:
                desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)
                if desk:
                    raise superdesk.SuperdeskError('Deleting default stages is not allowed.')


class TasksStageItemsResource(Resource):
    endpoint_name = 'tasks_stage_items'
    resource_title = endpoint_name
    url = 'stages/<regex("[a-zA-Z0-9:\\-\\.]+"):stage_id>/items'
    resource_methods = ['GET']
    item_methods = []
    datasource = TaskResource.datasource


class TasksStageItemsService(BaseService):

    custom_hateoas = {'self': {'title': 'Tasks', 'href': '/tasks/{_id}'}}

    def get(self, req, **lookup):
        stage_id = lookup['lookup']['stage_id']
        stage = superdesk.get_resource_service('stages').find_one(req=None, _id=stage_id)
        if not stage:
            raise superdesk.SuperdeskError(payload='Invalid stage id.')

        docs = superdesk.get_resource_service('tasks').get(req=req, lookup={'task.stage': stage_id})

        for doc in docs:
            build_custom_hateoas(self.custom_hateoas, doc)
        return docs
