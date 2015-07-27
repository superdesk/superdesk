# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


"""Media archive module"""

import logging

from .archive import ArchiveResource, ArchiveService, ArchiveVersionsResource, AutoSaveResource, \
    ArchiveSaveService
from .commands import RemoveExpiredSpikeContent
from .ingest import IngestResource, IngestService
from .item_comments import ItemCommentsResource, ItemCommentsSubResource, ItemCommentsService, ItemCommentsSubService
from .user_content import UserContentResource, UserContentService
from .archive_lock import ArchiveLockResource, ArchiveUnlockResource, ArchiveLockService, ArchiveUnlockService
from .archive_spike import ArchiveUnspikeResource, ArchiveSpikeService, ArchiveSpikeResource, ArchiveUnspikeService
import superdesk
from apps.common.components.utils import register_component
from apps.item_lock.components.item_lock import ItemLock
from apps.item_lock.components.item_hold import ItemHold
from apps.common.models.utils import register_model
from apps.item_lock.models.item import ItemModel
from apps.common.models.io.eve_proxy import EveProxy
from superdesk.celery_app import celery
from .saved_searches import SavedSearchesService, SavedSearchesResource, \
    SavedSearchItemsResource, SavedSearchItemsService
from .archive_link import ArchiveLinkResource, ArchiveLinkService
from .archive_rewrite import ArchiveRewriteResource, ArchiveRewriteService


logger = logging.getLogger(__name__)


def init_app(app):

    endpoint_name = 'ingest'
    service = IngestService(endpoint_name, backend=superdesk.get_backend())
    IngestResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_versions'
    service = superdesk.Service(endpoint_name, backend=superdesk.get_backend())
    ArchiveVersionsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive'
    service = ArchiveService(endpoint_name, backend=superdesk.get_backend())
    ArchiveResource(endpoint_name, app=app, service=service)

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

    endpoint_name = 'archive_unspike'
    service = ArchiveUnspikeService(endpoint_name, backend=superdesk.get_backend())
    ArchiveUnspikeResource(endpoint_name, app=app, service=service)

    endpoint_name = 'user_content'
    service = UserContentService(endpoint_name, backend=superdesk.get_backend())
    UserContentResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_link'
    service = ArchiveLinkService(endpoint_name, backend=superdesk.get_backend())
    ArchiveLinkResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_rewrite'
    service = ArchiveRewriteService(endpoint_name, backend=superdesk.get_backend())
    ArchiveRewriteResource(endpoint_name, app=app, service=service)

    endpoint_name = 'saved_searches'
    service = SavedSearchesService(endpoint_name, backend=superdesk.get_backend())
    SavedSearchesResource(endpoint_name, app=app, service=service)

    endpoint_name = 'saved_search_items'
    service = SavedSearchItemsService(endpoint_name, backend=superdesk.get_backend())
    SavedSearchItemsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'archive_autosave'
    service = ArchiveSaveService(endpoint_name, backend=superdesk.get_backend())
    AutoSaveResource(endpoint_name, app=app, service=service)

    from apps.item_autosave.components.item_autosave import ItemAutosave
    from apps.item_autosave.models.item_autosave import ItemAutosaveModel
    register_component(ItemLock(app))
    register_component(ItemHold(app))
    register_model(ItemModel(EveProxy(superdesk.get_backend())))
    register_component(ItemAutosave(app))
    register_model(ItemAutosaveModel(EveProxy(superdesk.get_backend())))

    superdesk.privilege(name='archive', label='Archive', description='User can view the published content.')
    superdesk.privilege(name='ingest', label='Ingest', description='User can view content in ingest and fetch it.')
    superdesk.privilege(name='spike', label='Spike', description='User can spike content.')
    superdesk.privilege(name='unspike', label='Un Spike', description='User can un-spike content.')
    superdesk.privilege(name='unlock', label='Unlock content', description='User can unlock content.')
    superdesk.privilege(name='metadata_uniquename', label='Edit Unique Name', description='User can edit unique name.')
    superdesk.privilege(name='saved_searches', label='Manage Saved Searches',
                        description='User can manage Saved Searches')

    superdesk.privilege(name='hold', label='Hold', description='Hold a content')
    superdesk.privilege(name='restore', label='Restore', description='Restore a hold a content')
    superdesk.privilege(name='rewrite', label='Rewrite', description='Rewrite a published content')

    superdesk.intrinsic_privilege(ArchiveUnlockResource.endpoint_name, method=['POST'])
    superdesk.intrinsic_privilege(ArchiveLinkResource.endpoint_name, method=['POST'])


@celery.task
def content_purge():
    RemoveExpiredSpikeContent().run()
