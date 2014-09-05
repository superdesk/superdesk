'''Media archive module'''
from .archive import ArchiveModel, ArchiveVersionsModel, AutoSaveModel
from .ingest import IngestModel
from .archive_media import ArchiveMediaModel
from .archive_ingest import ArchiveIngestModel
from .item_comments import ItemCommentsModel, ItemCommentsSubModel
from .user_content import UserContentModel
from .archive_lock import ArchiveLockModel, ArchiveUnlockModel
from .content_view import ContentViewModel, ContentViewItemsModel


def init_app(app):
    IngestModel(app=app)
    ArchiveVersionsModel(app=app)
    ArchiveModel(app=app)
    ArchiveMediaModel(app=app)
    ArchiveIngestModel(app=app)
    ItemCommentsModel(app=app)
    ItemCommentsSubModel(app=app)
    ArchiveLockModel(app)
    ArchiveUnlockModel(app)
    UserContentModel(app)
    ContentViewModel(app=app)
    ContentViewItemsModel(app=app)
    AutoSaveModel(app)
