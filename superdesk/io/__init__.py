"""Superdesk IO"""
import logging
import superdesk

from superdesk.celery_app import celery
from superdesk.etree import etree, ParseError


parsers = []
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


@celery.task()
def update_ingest():
    UpdateIngest().run()


@celery.task()
def gc_ingest():
    RemoveExpiredContent().run()


class ParserRegistry(type):
    """Registry metaclass for parsers."""

    def __init__(cls, name, bases, attrs):
        """Register sub-classes of Parser class when defined."""
        super(ParserRegistry, cls).__init__(name, bases, attrs)
        if name != 'Parser':
            parsers.append(cls())


class Parser(metaclass=ParserRegistry):
    """Base Parser class for all types of Parsers like News ML 1.2, News ML G2, NITF, etc."""

    def parse_message(self, xml):
        """Parse the ingest XML and extracts the relevant elements/attributes values from the XML."""
        raise NotImplementedError()

    def can_parse(self, xml):
        """Test if parser can parse given xml."""
        raise NotImplementedError()


def get_xml_parser(etree):
    """Get parser for given xml.

    :param etree: parsed xml
    """
    for parser in parsers:
        if parser.can_parse(etree):
            return parser


# must be imported for registration
import superdesk.io.nitf
import superdesk.io.newsml_2_0
import superdesk.io.newsml_1_2

superdesk.privilege(name='ingest_providers', label='Ingest Channels', description='User can maintain Ingest Channels.')
