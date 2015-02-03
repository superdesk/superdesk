# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from ..models.item_autosave import ItemAutosaveModel
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.item_lock.models.item import ItemModel
from superdesk.errors import SuperdeskApiError


class ItemAutosave(BaseComponent):
    def __init__(self, app):
        self.app = app
        self.app.on_item_locked += self.on_item_locked

    @classmethod
    def name(cls):
        return 'archive_autosave'

    def autosave(self, item_id, updates, user, etag):
        item_model = get_model(ItemModel)
        item = item_model.find_one({'_id': item_id})
        if item is None:
            raise SuperdeskApiError.notFoundError('Invalid item identifier')

        lock_user = item.get('lock_user', None)
        if lock_user and str(lock_user) != str(user['_id']):
            raise SuperdeskApiError.forbiddenError('The item was locked by another user')

        autosave_model = get_model(ItemAutosaveModel)
        item.update(updates)
        self.app.on_item_autosave(item)
        autosave_item = autosave_model.find_one({'_id': item_id})
        if not autosave_item:
            autosave_model.create([item])
        else:
            autosave_model.update({'_id': item_id}, item, etag)
        self.app.on_item_autosaved(item)
        updates.update(item)
        return updates

    def clear(self, item_id):
        autosave_model = get_model(ItemAutosaveModel)
        return autosave_model.delete({'_id': item_id})

    def on_item_locked(self, item, user):
        lock_user = item.get('lock_user', None)
        if str(lock_user) != str(user):
            self.clear(item['_id'])
