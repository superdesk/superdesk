"""Superdesk IO"""

import logging
import superdesk
from superdesk.celery_app import celery
from .reuters import ReutersUpdateService, PROVIDER as ReutersName
from .aap import AAPIngestService, PROVIDER as AAPName
from .afp import AFPIngestService, PROVIDER as AFPName

logger = logging.getLogger(__name__)
providers = {}
allowed_providers = []


def init_app(app):
    from .ingest_provider_model import IngestProviderModel
    IngestProviderModel(app=app)


def register_provider(type, provider):
    providers[type] = provider
    allowed_providers.append(type)


register_provider(ReutersName, ReutersUpdateService())
register_provider(AAPName, AAPIngestService())
register_provider(AFPName, AFPIngestService())

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
