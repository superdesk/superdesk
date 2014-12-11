"""Superdesk IO"""
import logging
import superdesk

from abc import ABCMeta, abstractmethod
from superdesk.celery_app import celery
from superdesk.etree import etree, ParseError


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


def get_text_word_count(text):
    """Get word count for given plain text.

    :param text: text string
    """
    return len(text.split())


def get_word_count(html):
    """Get word count for given html.

    :param html: html string to count
    """
    try:
        root = etree.fromstringlist('<doc>{0}</doc>'.format(html))
        text = etree.tostring(root, encoding='unicode', method='text')
        return get_text_word_count(text)
    except ParseError:
        return get_text_word_count(html)


superdesk.privilege(name='ingest_providers', label='Ingest Channels', description='User can maintain Ingest Channels.')


@celery.task()
def update_ingest():
    UpdateIngest().run()


@celery.task()
def gc_ingest():
    RemoveExpiredContent().run()


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
