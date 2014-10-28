from superdesk.resource import Resource
from apps.archive.common import base_schema, item_url
from superdesk.services import BaseService
from apps.common.models.utils import get_model
from apps.legal_archive.models.legal_archive import LegalArchiveModel


class LegalArchiveResource(Resource):
    endpoint_name = 'legal_archive'
    schema = base_schema
    schema['type'] = {'type': 'string'}
    item_url = item_url
    resource_methods = ['GET']
    item_methods = ['GET']
    resource_title = endpoint_name


class LegalArchiveService(BaseService):
    def get(self, req, lookup):
        return get_model(LegalArchiveModel).find(lookup)


class ErrorsResource(Resource):
    endpoint_name = 'errors'
    schema = {
        'resource': {'type': 'string'},
        'docs': {'type': 'list'},
        'result': {'type': 'string'}
    }
    resource_methods = []
    item_methods = []
    resource_title = endpoint_name
