'''Media archive module'''
from .archive import ArchiveModel, ArchiveVersionsModel
from .ingest import IngestModel
from .archive_media import ArchiveMediaModel
from .archive_ingest import ArchiveIngestModel


def init_app(app):
    IngestModel(app=app)
    ArchiveVersionsModel(app=app)
    ArchiveModel(app=app)
    ArchiveMediaModel(app=app)
    ArchiveIngestModel(app=app)
