'''Media archive module'''
from .archive import ArchiveModel, ArchiveVersionsModel
from .ingest import IngestModel
from .archive_media import ArchiveMediaModel
from .archive_ingest import ArchiveIngestModel
from .item_comments import ItemCommentsModel, ItemCommentsSubModel
from .user_content import UserContentModel
from .archive_lock import ArchiveLockModel, ArchiveUnlockModel
from .content_view import ContentViewModel, ContentViewItemsModel
from ..archive.archive import ArchiveAutosaveModel
from ..common.components.utils import register_component
from ..item_lock.components.item_lock import ItemLock
from ..common.models.utils import register_model
from ..item_lock.models.item import ItemModel
from ..common.models.io.eve_proxy import EveProxy
from ..item_autosave.components.item_autosave import ItemAutosave
from ..item_autosave.models.item_autosave import ItemAutosaveModel


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
    ArchiveAutosaveModel(app)
    register_component(ItemLock(app))
    register_model(ItemModel(EveProxy(app.data)))
    register_component(ItemAutosave(app))
    register_model(ItemAutosaveModel(EveProxy(app.data)))
