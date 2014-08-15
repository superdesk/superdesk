'''Media archive module'''
from .archive import ArchiveModel, ArchiveVersionsModel
from .ingest import IngestModel
from .archive_media import ArchiveMediaModel
from .archive_ingest import ArchiveIngestModel
from .item_comments import ItemCommentsModel, ItemCommentsSubModel
from .content_view import ContentViewModel
from .user_content import UserContentModel
from superdesk.archive.archive_lock import ArchiveLockModel, ArchiveUnlockModel


def init_app(app):
    IngestModel(app=app)
    ArchiveVersionsModel(app=app)
    ArchiveModel(app=app)
    ArchiveMediaModel(app=app)
    ArchiveIngestModel(app=app)
    ItemCommentsModel(app=app)
    ItemCommentsSubModel(app=app)
    ContentViewModel(app=app)
    ArchiveLockModel(app)
    ArchiveUnlockModel(app)
    UserContentModel(app)
