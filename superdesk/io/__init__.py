"""Superdesk IO"""

import logging
import superdesk
from superdesk.models import BaseModel
from superdesk.celery_app import celery
from .reuters import ReutersUpdateService, PROVIDER as ReutersName
from .aap import AAPIngestService, PROVIDER as AAPName
from .afp import AFPIngestService, PROVIDER as AFPName

DAYS_TO_KEEP = 2
logger = logging.getLogger(__name__)
providers = {}


def register_provider(type, provider):
    providers[type] = provider

superdesk.provider = register_provider

superdesk.provider(ReutersName, ReutersUpdateService())
superdesk.provider(AAPName, AAPIngestService())
superdesk.provider(AFPName, AFPIngestService())

from .commands.remove_expired_content import RemoveExpiredContent
from .commands.update_ingest import UpdateIngest
from .commands.add_provider import AddProvider  # NOQA
import superdesk.io.subjectcodes  # NOQA


@celery.task()
def fetch_ingest():
    try:
        RemoveExpiredContent().run()
    except Exception as ex:
        logger.error(ex)
    UpdateIngest().run()


def init_app(app):
    IngestProviderModel(app=app)


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
            'allowed': providers.keys()
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
