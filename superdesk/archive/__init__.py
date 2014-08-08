'''Media archive module'''
from .archive import ArchiveModel, ArchiveVersionsModel
from .ingest import IngestModel
from .archive_media import ArchiveMediaModel, AuthorItemModel
from .archive_ingest import ArchiveIngestModel
from .item_comments import ItemCommentsModel, ItemCommentsSubModel
from superdesk.archive.archive_lock import ArchiveLockModel
from .content_view import ContentViewModel, ContentViewItemsModel


def init_app(app):
    IngestModel(app=app)
    ArchiveVersionsModel(app=app)
    ArchiveModel(app=app)
    ArchiveMediaModel(app=app)
    ArchiveIngestModel(app=app)
    AuthorItemModel(app=app)
    ItemCommentsModel(app=app)
    ItemCommentsSubModel(app=app)
    ContentViewModel(app=app)
    ArchiveLockModel(app=app)
    ContentViewItemsModel(app=app)
