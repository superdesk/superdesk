"""Superdesk IO"""

import logging
from superdesk.celery_app import celery


providers = {}
allowed_providers = []
logger = logging.getLogger(__name__)


class IngestService():
    """Base ingest service class."""

    def get_items(self, guid):
        raise LookupError()

    def update(self, provider):
        raise NotImplementedError()


from .commands.remove_expired_content import RemoveExpiredContent
from .commands.update_ingest import UpdateIngest
from .commands.add_provider import AddProvider  # NOQA


def init_app(app):
    from .ingest_provider_model import IngestProviderResource
    from superdesk.services import BaseService
    import superdesk
    endpoint_name = 'ingest_providers'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    IngestProviderResource(endpoint_name, app=app, service=service)


def register_provider(type, provider):
    providers[type] = provider
    allowed_providers.append(type)


@celery.task()
def fetch_ingest():
    try:
        RemoveExpiredContent().run()
    except Exception as ex:
        logger.error(ex)
    UpdateIngest().run()
