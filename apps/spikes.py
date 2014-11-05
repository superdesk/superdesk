from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend
from apps.content import metadata_schema

_preferences_key = 'preferences'
_user_preferences_key = 'user_preferences'
_session_preferences_key = 'session_preferences'


def init_app(app):
    endpoint_name = 'spikes'
    service = SpikesService(endpoint_name, backend=get_backend())
    SpikesResource(endpoint_name, app=app, service=service)


class SpikesResource(Resource):
    schema = metadata_schema
    datasource = {
        'source': 'archive',
        'search_backend': 'elastic',
        'default_sort': [('expiry', -1)],
        'elastic_filter': {'term': {'is_spiked': True}}
    }
    resource_methods = ['GET']


class SpikesService(BaseService):

    def get(self, req, lookup):
        docs = super().get(req, lookup)
        return docs
