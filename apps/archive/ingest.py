from settings import MAX_VALUE_OF_INGEST_SEQUENCE
from superdesk.celery_app import update_key, set_key
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.workflow import set_default_state
from apps.content import metadata_schema
from .common import extra_response_fields, item_url, aggregations, on_create_item


STATE_INGESTED = 'ingested'
SOURCE = 'ingest'


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

    def set_ingest_provider_sequence(self, item, provider):
        """
        Sets the value of ingest_provider_sequence in item.
        :param item: object to which ingest_provider_sequence to be set
        :param provider: ingest_provider object, used to build the key name of sequence
        """

        sequence_key_name = "{provider_type}_{provider_id}_ingest_seq".format(provider_type=provider.get('type'),
                                                                              provider_id=str(provider.get('_id')))
        sequence_number = update_key(sequence_key_name, flag=True)
        item['ingest_provider_sequence'] = str(sequence_number)

        if sequence_number == MAX_VALUE_OF_INGEST_SEQUENCE:
            set_key(sequence_key_name)
