import superdesk

from apps.text_archive.text_archive import TextArchiveResource, TextArchiveService
from .import_text_archive.import_command import AppImportTextArchiveCommand  # noqa


def init_app(app):

    endpoint_name = 'text_archive'
    service = TextArchiveService(endpoint_name, backend=superdesk.get_backend())
    TextArchiveResource(endpoint_name, app=app, service=service)
