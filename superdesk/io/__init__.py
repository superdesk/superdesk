"""Superdesk IO"""
from abc import ABCMeta, abstractmethod
import superdesk
import logging

from superdesk.celery_app import celery


providers = {}
allowed_providers = []
logger = logging.getLogger(__name__)

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


superdesk.privilege(name='ingest_providers', label='Ingest Channels', description='User can maintain Ingest Channels.')


@celery.task()
def fetch_ingest():
    RemoveExpiredContent().run()
    UpdateIngest().run()


class Parser:
    """
    Parent Class for all types of Parsers like News ML 1.2, News ML G2, NITF,...
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse_message(self, xml_doc):
        """
        Parses the ingest XML and extracts the relevant elements/attributes values from the XML.
        Sub-classes must override.
        """
