'''Media archive module'''
from .archive import ArchiveModel
from .ingest import IngestModel
from .archive_media import ArchiveMediaModel
from .archive_ingest import ArchiveIngestModel
from superdesk.archive.archive import ArchiveVersionsModel


def init_app(app):
    IngestModel(app=app)
    ArchiveVersionsModel(app=app)
    ArchiveModel(app=app)
    ArchiveMediaModel(app=app)
    ArchiveIngestModel(app=app)
