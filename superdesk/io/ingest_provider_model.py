
from superdesk.models import BaseModel
from superdesk.io import allowed_providers
DAYS_TO_KEEP = 2


class IngestProviderModel(BaseModel):
    endpoint_name = 'ingest_providers'
    schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'type': {
            'type': 'string',
            'required': True,
            'allowed': allowed_providers
        },
        'days_to_keep': {
            'type': 'integer',
            'required': True,
            'default': DAYS_TO_KEEP
        },
        'config': {
            'type': 'dict'
        },
        'ingested_count': {
            'type': 'integer'
        },
        'accepted_count': {
            'type': 'integer'
        },
        'token': {
            'type': 'dict'
        }
    }
