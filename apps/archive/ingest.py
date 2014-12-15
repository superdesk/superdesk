from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.workflow import set_default_state
from apps.content import metadata_schema
from .common import extra_response_fields, item_url, aggregations, on_create_item


STATE_INGESTED = 'ingested'


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

    def create(self, docs):
        for doc in docs:
            set_default_state(doc, STATE_INGESTED)
        on_create_item(docs)  # do it after setting the state otherwise it will make it draft
        return super().create(docs)
