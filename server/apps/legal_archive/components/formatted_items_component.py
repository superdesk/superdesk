# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.common.components.utils import get_component
from apps.legal_archive.components.error import Error
from apps.legal_archive.models.formatted_items_model import FormattedItemsModel


class FormattedItems(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'formatted_item'

    def find(self, filter, projection=None, **options):
        try:
            return get_model(FormattedItemsModel).find(filter, projection, **options)
        except Exception as e:
            get_component(Error).create(FormattedItemsModel.name(), filter, str(e))

    def create(self, items):
        try:
            return get_model(FormattedItemsModel).create(items)
        except Exception as e:
            get_component(Error).create(FormattedItemsModel.name(), items, str(e))

    def update(self, filter, doc, etag=None):
        try:
            return get_model(FormattedItemsModel).update(filter, doc, etag)
        except Exception as e:
            get_component(Error).create(FormattedItemsModel.name(), doc, str(e))

    def delete(self, filter):
        try:
            return get_model(FormattedItemsModel).update(filter)
        except Exception as e:
            get_component(Error).create(FormattedItemsModel.name(), filter, str(e))
