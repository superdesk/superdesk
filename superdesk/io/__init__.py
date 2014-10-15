"""Superdesk IO"""

import logging
import os
import shutil
from superdesk.utc import utcnow
from superdesk.celery_app import celery
from datetime import timedelta

providers = {}
allowed_providers = []
logger = logging.getLogger(__name__)


class IngestService():
    """Base ingest service class."""

    def get_items(self, guid):
        raise LookupError()

    def update(self, provider):
        raise NotImplementedError()

    def move_file(self, filepath, filename, success=True):
        try:
            if not os.path.exists(os.path.join(filepath, "_PROCESSED/")):
                os.makedirs(os.path.join(filepath, "_PROCESSED/"))
            if not os.path.exists(os.path.join(filepath, "_ERROR/")):
                os.makedirs(os.path.join(filepath, "_ERROR/"))

            if success:
                shutil.copy2(os.path.join(filepath, filename), os.path.join(filepath, "_PROCESSED/"))
            else:
                shutil.copy2(os.path.join(filepath, filename), os.path.join(filepath, "_ERROR/"))
        finally:
            os.remove(os.path.join(filepath, filename))

    def is_latest_content(self, last_updated, provider_last_updated=None):
        """Parse file only if it's not older than provider last update -10m"""

        if not provider_last_updated:
            provider_last_updated = utcnow() - timedelta(days=2)

        return provider_last_updated - timedelta(minutes=10) < last_updated


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
