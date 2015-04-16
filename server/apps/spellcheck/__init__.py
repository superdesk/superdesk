
from .spellcheck import SpellcheckService, SpellcheckResource


def init_app(app):
    endpoint_name = 'spellcheck'
    service = SpellcheckService(endpoint_name, backend=None)
    SpellcheckResource(endpoint_name, app=app, service=service)
