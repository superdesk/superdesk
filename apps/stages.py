import logging
from superdesk.resource import Resource
from superdesk.services import BaseService
import superdesk


logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'stages'
    service = StagesService(endpoint_name, backend=superdesk.get_backend())
    StagesResource(endpoint_name, app=app, service=service)


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

    privileges = {'POST': 'desks', 'DELETE': 'desks', 'PATCH': 'desks'}


class StagesService(BaseService):

    def on_delete(self, doc):
        if doc['default_incoming'] is True:
            desk_id = doc.get('desk', None)
            if desk_id:
                desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)
                if desk:
                    raise superdesk.SuperdeskError('Deleting default stages is not allowed.')
