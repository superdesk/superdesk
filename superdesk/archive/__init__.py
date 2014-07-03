'''Media archive module'''
from .archive import ArchiveModel
from .ingest import IngestModel
from .archive_media import ArchiveMediaModel


def init_app(app):
    IngestModel(app=app)
    ArchiveModel(app=app)
    ArchiveMediaModel(app=app)
