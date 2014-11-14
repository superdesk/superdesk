from superdesk.resource import Resource
from .common import extra_response_fields, item_url, aggregations
from .common import on_create_item
from superdesk.services import BaseService
from apps.content import metadata_schema


class IngestResource(Resource):
    schema = {
        'archived': {
            'type': 'datetime'
        }
    }
    schema.update(metadata_schema)
    extra_response_fields = extra_response_fields
    item_url = item_url
    datasource = {
        'search_backend': 'elastic',
        'aggregations': aggregations
    }


class IngestService(BaseService):

    def on_create(self, docs):
        on_create_item(docs)
