from superdesk import get_backend

from . import ingest_provider  # NOQA
from .code_request_resource import (
    WhatsAppCodeRequestResource, WhatsAppCodeRequestService
)
from .registration_request_resource import (
    WhatsAppRegistrationRequestResource, WhatsAppRegistrationRequestService
)


def init_app(app):
    endpoint_name = 'whatsapp_code_request'
    service = WhatsAppCodeRequestService(endpoint_name, backend=get_backend())
    WhatsAppCodeRequestResource(endpoint_name, app=app, service=service)

    endpoint_name = 'whatsapp_registration_request'
    service = WhatsAppRegistrationRequestService(endpoint_name, backend=get_backend())
    WhatsAppRegistrationRequestResource(endpoint_name, app=app, service=service)
