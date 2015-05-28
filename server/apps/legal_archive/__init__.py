# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.legal_archive.components.archive_component import LegalArchive
from apps.common.components.utils import register_component
from apps.common.models.utils import register_model
from apps.legal_archive.components.archive_versions_component import LegalArchiveVersions
from apps.legal_archive.components.formatted_items_component import FormattedItems
from apps.legal_archive.components.publish_queue_component import PublishQueue
from apps.legal_archive.models.archive_model import LegalArchiveModel
from apps.legal_archive.datalayer import LegalArchiveDataLayer
from apps.legal_archive.models.archive_versions_model import LegalArchiveVersionsModel
from apps.legal_archive.models.formatted_items_model import FormattedItemsModel
from apps.legal_archive.models.publish_queue_model import PublishQueueModel
from apps.legal_archive.resource import ErrorsResource
from apps.legal_archive.components.error import Error
from apps.legal_archive.models.errors import ErrorsModel
from superdesk.services import BaseService
from apps.common.models.io.eve_proxy import EveProxy


def init_app(app):
    data_layer = LegalArchiveDataLayer(app)

    register_model(LegalArchiveModel(EveProxy(data_layer)))
    register_component(LegalArchive(app))

    register_model(LegalArchiveVersionsModel(EveProxy(data_layer)))
    register_component(LegalArchiveVersions(app))

    register_model(FormattedItemsModel(EveProxy(data_layer)))
    register_component(FormattedItems(app))

    register_model(PublishQueueModel(EveProxy(data_layer)))
    register_component(PublishQueue(app))

    register_model(ErrorsModel(EveProxy(data_layer)))
    register_component(Error(app))

    endpoint_name = 'errors'
    service = BaseService(endpoint_name, backend=data_layer)
    ErrorsResource(endpoint_name, app=app, service=service)
