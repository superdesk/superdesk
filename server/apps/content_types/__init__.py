
import superdesk
from .content_types import ContentTypesResource, ContentTypesService, CONTENT_TYPE_PRIVILEGE


def init_app(app):
    endpoint_name = 'content_types'
    service = ContentTypesService(endpoint_name, backend=superdesk.get_backend())
    ContentTypesResource(endpoint_name, app=app, service=service)
    superdesk.privilege(name=CONTENT_TYPE_PRIVILEGE,
                        label='Content Types',
                        description='Manage types')
