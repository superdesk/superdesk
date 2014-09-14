'''Media archive module'''
from .archive import ArchiveModel, ArchiveService, ArchiveVersionsModel, AutoSaveModel, \
    ArchiveVersionsService, ArchiveSaveService
from .ingest import IngestModel, IngestService
from .archive_media import ArchiveMediaModel, ArchiveMediaService
from .archive_ingest import ArchiveIngestModel, ArchiveIngestService
from .item_comments import ItemCommentsModel, ItemCommentsSubModel, ItemCommentsService, ItemCommentsSubService
from .user_content import UserContentModel, UserContentService
from .archive_lock import ArchiveLockModel, ArchiveUnlockModel, ArchiveLockService, ArchiveUnlockService
from .content_view import ContentViewModel, ContentViewItemsModel, ContentViewService, ContentViewItemsService
import superdesk
from apps.common.components.utils import register_component
from apps.item_lock.components.item_lock import ItemLock
from apps.common.models.utils import register_model
from apps.item_lock.models.item import ItemModel
from apps.common.models.io.eve_proxy import EveProxy
from apps.item_autosave.components.item_autosave import ItemAutosave
from apps.item_autosave.models.item_autosave import ItemAutosaveModel


def init_app(app):

    endpoint_name = 'ingest'
    service = IngestService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    IngestModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'archive_versions'
    service = ArchiveVersionsService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ArchiveVersionsModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'archive'
    service = ArchiveService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ArchiveModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'archive_media'
    service = ArchiveMediaService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ArchiveMediaModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'archive_ingest'
    service = ArchiveIngestService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ArchiveIngestModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'item_comments'
    service = ItemCommentsService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ItemCommentsModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'content_item_comments'
    service = ItemCommentsSubService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ItemCommentsSubModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'archive_lock'
    service = ArchiveLockService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ArchiveLockModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'archive_unlock'
    service = ArchiveUnlockService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ArchiveUnlockModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'user_content'
    service = UserContentService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    UserContentModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'content_view'
    service = ContentViewService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ContentViewModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'content_view_items'
    service = ContentViewItemsService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    ContentViewItemsModel(endpoint_name=endpoint_name, app=app, service=service)

    endpoint_name = 'autosave'
    service = ArchiveSaveService(endpoint_name=endpoint_name, backend=superdesk.get_backend())
    AutoSaveModel(endpoint_name=endpoint_name, app=app, service=service)

    register_component(ItemLock(app))
    register_model(ItemModel(EveProxy(app.data)))
    register_component(ItemAutosave(app))
    register_model(ItemAutosaveModel(EveProxy(app.data)))
