'''Media archive module'''
from .archive import ArchiveResource, ArchiveService, ArchiveVersionsResource, AutoSaveResource, \
    ArchiveVersionsService, ArchiveSaveService
from .ingest import IngestResource, IngestService
from .archive_media import ArchiveMediaResource, ArchiveMediaService
from .archive_ingest import ArchiveIngestResource, ArchiveIngestService
from .item_comments import ItemCommentsResource, ItemCommentsSubResource, ItemCommentsService, ItemCommentsSubService
from .user_content import UserContentResource, UserContentService
from .archive_lock import ArchiveLockResource, ArchiveUnlockResource, ArchiveLockService, ArchiveUnlockService
from .content_view import ContentViewResource, ContentViewItemsResource, ContentViewService, ContentViewItemsService
import superdesk
from apps.common.components.utils import register_component
from apps.item_lock.components.item_lock import ItemLock
from apps.common.models.utils import register_model
from apps.item_lock.models.item import ItemModel
from apps.common.models.io.eve_proxy import EveProxy


def init_app(app):

    endpoint_name = 'ingest'
    service = IngestService(endpoint_name, backend=superdesk.get_backend())
    IngestResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_versions'
    service = ArchiveVersionsService(endpoint_name, backend=superdesk.get_backend())
    ArchiveVersionsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive'
    service = ArchiveService(endpoint_name, backend=superdesk.get_backend())
    ArchiveResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_media'
    service = ArchiveMediaService(endpoint_name, backend=superdesk.get_backend())
    ArchiveMediaResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_ingest'
    service = ArchiveIngestService(endpoint_name, backend=superdesk.get_backend())
    ArchiveIngestResource(endpoint_name, app=app, service=service)

    endpoint_name = 'item_comments'
    service = ItemCommentsService(endpoint_name, backend=superdesk.get_backend())
    ItemCommentsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'content_item_comments'
    service = ItemCommentsSubService(endpoint_name, backend=superdesk.get_backend())
    ItemCommentsSubResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_lock'
    service = ArchiveLockService(endpoint_name, backend=superdesk.get_backend())
    ArchiveLockResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_unlock'
    service = ArchiveUnlockService(endpoint_name, backend=superdesk.get_backend())
    ArchiveUnlockResource(endpoint_name, app=app, service=service)

    endpoint_name = 'user_content'
    service = UserContentService(endpoint_name, backend=superdesk.get_backend())
    UserContentResource(endpoint_name, app=app, service=service)

    endpoint_name = 'content_view'
    service = ContentViewService(endpoint_name, backend=superdesk.get_backend())
    ContentViewResource(endpoint_name, app=app, service=service)

    endpoint_name = 'content_view_items'
    service = ContentViewItemsService(endpoint_name, backend=superdesk.get_backend())
    ContentViewItemsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_autosave'
    service = ArchiveSaveService(endpoint_name, backend=superdesk.get_backend())
    AutoSaveResource(endpoint_name, app=app, service=service)

    from apps.item_autosave.components.item_autosave import ItemAutosave
    from apps.item_autosave.models.item_autosave import ItemAutosaveModel
    register_component(ItemLock(app))
    register_model(ItemModel(EveProxy(app.data)))
    register_component(ItemAutosave(app))
    register_model(ItemAutosaveModel(EveProxy(app.data)))
