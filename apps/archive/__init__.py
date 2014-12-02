"""Media archive module"""

from .archive import ArchiveResource, ArchiveService, ArchiveVersionsResource, AutoSaveResource, \
    ArchiveVersionsService, ArchiveSaveService
from .ingest import IngestResource, IngestService
from .archive_media import ArchiveMediaResource, ArchiveMediaService, ArchiveMediaVersionsResource
from .archive_ingest import ArchiveIngestResource, ArchiveIngestService
from .item_comments import ItemCommentsResource, ItemCommentsSubResource, ItemCommentsService, ItemCommentsSubService
from .user_content import UserContentResource, UserContentService
from .archive_lock import ArchiveLockResource, ArchiveUnlockResource, ArchiveLockService, ArchiveUnlockService
from .archive_spike import ArchiveSpikeResource, ArchiveSpikeService
from .content_view import ContentViewResource, ContentViewItemsResource, ContentViewService, ContentViewItemsService
import superdesk
from apps.common.components.utils import register_component
from apps.item_lock.components.item_lock import ItemLock
from apps.item_lock.components.item_spike import ItemSpike
from apps.common.models.utils import register_model
from apps.item_lock.models.item import ItemModel
from apps.common.models.io.eve_proxy import EveProxy
from superdesk.celery_app import celery
import logging
from .archive_spike import ArchiveRemoveExpiredSpikes


logger = logging.getLogger(__name__)


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

    endpoint_name = 'archive_media_versions'
    service = ArchiveVersionsService(endpoint_name, backend=superdesk.get_backend())
    ArchiveMediaVersionsResource(endpoint_name, app=app, service=service)

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

    endpoint_name = 'archive_spike'
    service = ArchiveSpikeService(endpoint_name, backend=superdesk.get_backend())
    ArchiveSpikeResource(endpoint_name, app=app, service=service)

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
    register_component(ItemSpike(app))
    register_model(ItemModel(EveProxy(superdesk.get_backend())))
    register_component(ItemAutosave(app))
    register_model(ItemAutosaveModel(EveProxy(superdesk.get_backend())))

    superdesk.privilege(name='archive', label='Archive', description='User can view the published content.')
    superdesk.privilege(name='ingest', label='Ingest', description='User can view content in ingest and fetch it.')
    superdesk.privilege(name='spike', label='Spike', description='User can spike content.')
    superdesk.privilege(name='unspike', label='Un Spike', description='User can un-spike content.')
    superdesk.privilege(name='unlock', label='Unlock content', description='User can unlock content.')
    superdesk.privilege(name='metadata_uniquename', label='Edit Unique Name', description='User can edit unique name.')
    superdesk.privilege(name='ingest_move', label='Move Content To Desk', description='Move Content to a Desk.')


@celery.task()
def spike_purge():
    ArchiveRemoveExpiredSpikes().run()
