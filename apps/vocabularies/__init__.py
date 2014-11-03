from .command import VocabulariesPopulateCommand
from .vocabularies import VocabulariesResource, VocabulariesService
import superdesk

def init_app(app):
    endpoint_name = 'vocabularies'
    service = VocabulariesService(endpoint_name, backend=superdesk.get_backend())
    VocabulariesResource(endpoint_name, app=app, service=service)