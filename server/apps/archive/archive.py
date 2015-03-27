# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from apps.users.services import current_user_has_privilege


SOURCE = 'archive'

import flask
from superdesk.resource import Resource
from .common import extra_response_fields, item_url, aggregations, remove_unwanted, update_state, set_item_expiry, \
    is_update_allowed
from .common import on_create_item, on_duplicate_item, generate_unique_id_and_name
from .common import get_user
from flask import current_app as app
from werkzeug.exceptions import NotFound
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.utc import utcnow
from eve.versioning import resolve_document_version
from superdesk.activity import add_activity, ACTIVITY_CREATE, ACTIVITY_UPDATE, ACTIVITY_DELETE
from eve.utils import parse_request, config
from superdesk.services import BaseService
from apps.users.services import is_admin
from apps.content import metadata_schema
from apps.common.components.utils import get_component
from apps.item_autosave.components.item_autosave import ItemAutosave
from apps.common.models.base_model import InvalidEtag
from apps.legal_archive.components.legal_archive_proxy import LegalArchiveProxy
from superdesk.etree import get_word_count
from superdesk.notification import push_notification
from copy import copy
import superdesk
import logging
from apps.common.models.utils import get_model
from apps.item_lock.models.item import ItemModel
from .archive_composite import PackageService
from .archive_media import ArchiveMediaService

logger = logging.getLogger(__name__)


def get_subject(doc1, doc2=None):
    for key in ('headline', 'subject', 'slugline'):
        value = doc1.get(key)
        if not value and doc2:
            value = doc2.get(key)
        if value:
            return value


def private_content_filter():
    """Filter out out users private content if this is a user request.

    As private we treat items where user is creator, last version creator,
    or has the item assigned to him atm.

    Also filter out content of stages not visible to current user (if any).
    """
    user = getattr(flask.g, 'user', None)
    if user:
        private_filter = {'should': [
            {'exists': {'field': 'task.desk'}},
            {'term': {'task.user': str(user['_id'])}},
            {'term': {'version_creator': str(user['_id'])}},
            {'term': {'original_creator': str(user['_id'])}},
        ]}

        stages = get_resource_service('users').get_invisible_stages_ids(user.get('_id'))
        if stages:
            private_filter['must_not'] = [{'terms': {'task.stage': stages}}]

        return {'bool': private_filter}


class ArchiveVersionsResource(Resource):
    schema = metadata_schema
    extra_response_fields = extra_response_fields
    item_url = item_url
    resource_methods = []
    internal_resource = True
    privileges = {'PATCH': 'archive'}


class ArchiveResource(Resource):
    schema = {
        'old_version': {
            'type': 'number',
        },
        'last_version': {
            'type': 'number',
        },
        'task': {'type': 'dict'}
    }

    schema.update(metadata_schema)
    extra_response_fields = extra_response_fields
    item_url = item_url
    datasource = {
        'search_backend': 'elastic',
        'aggregations': aggregations,
        'projection': {
            'old_version': 0,
            'last_version': 0
        },
        'default_sort': [('_updated', -1)],
        'elastic_filter_callback': private_content_filter
    }
    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH', 'PUT']
    versioning = True
    privileges = {'POST': 'archive', 'PATCH': 'archive', 'PUT': 'archive'}


def update_word_count(doc):
    """Update word count if there was change in content.

    :param doc: created/udpated document
    """
    if doc.get('body_html'):
        doc.setdefault('word_count', get_word_count(doc.get('body_html')))


class ArchiveService(BaseService):
    packageService = PackageService()
    mediaService = ArchiveMediaService()

    def on_create(self, docs):
        on_create_item(docs)

        for doc in docs:
            doc['version_creator'] = doc['original_creator']
            remove_unwanted(doc)
            update_word_count(doc)
            set_item_expiry({}, doc)

            if doc['type'] == 'composite':
                self.packageService.on_create([doc])

            if doc.get('media'):
                self.mediaService.on_create([doc])

    def on_created(self, docs):
        packages = [doc for doc in docs if doc['type'] == 'composite']
        if packages:
            self.packageService.on_created(packages)

        get_component(LegalArchiveProxy).create(docs)
        user = get_user()
        for doc in docs:
            subject = get_subject(doc)
            if subject:
                msg = 'added new {{ type }} item about "{{ subject }}"'
            else:
                msg = 'added new {{ type }} item with empty header/title'
            add_activity(ACTIVITY_CREATE, msg,
                         self.datasource, item=doc, type=doc['type'], subject=subject)
            push_notification('item:created', item=str(doc['_id']), user=str(user.get('_id')))

    def on_update(self, updates, original):
        is_update_allowed(original)
        user = get_user()

        if 'unique_name' in updates and not is_admin(user) \
                and (user['active_privileges'].get('metadata_uniquename', 0) == 0):
            raise SuperdeskApiError.forbiddenError("Unauthorized to modify Unique Name")

        remove_unwanted(updates)

        if self.__is_req_for_save(updates):
            update_state(original, updates)

        lock_user = original.get('lock_user', None)
        force_unlock = updates.get('force_unlock', False)

        original_creator = updates.get('original_creator', None)
        if not original_creator:
            updates['original_creator'] = original['original_creator']

        str_user_id = str(user.get('_id'))
        if lock_user and str(lock_user) != str_user_id and not force_unlock:
            raise SuperdeskApiError.forbiddenError('The item was locked by another user')

        updates['versioncreated'] = utcnow()
        set_item_expiry(updates, original)
        updates['version_creator'] = str_user_id
        update_word_count(updates)

        if force_unlock:
            del updates['force_unlock']

        if original['type'] == 'composite':
            self.packageService.on_update(updates, original)

    def on_updated(self, updates, original):
        get_component(ItemAutosave).clear(original['_id'])
        get_component(LegalArchiveProxy).update(original, updates)

        if original['type'] == 'composite':
            self.packageService.on_updated(updates, original)

        user = get_user()
        if '_version' in updates:
            updated = copy(original)
            updated.update(updates)
            add_activity(ACTIVITY_UPDATE, 'created new version {{ version }} for item {{ type }} about "{{ subject }}"',
                         self.datasource, item=updated,
                         version=updates['_version'], subject=get_subject(updates, original),
                         type=updated['type'])
            push_notification('item:updated', item=str(original['_id']), user=str(user.get('_id')))

    def on_replace(self, document, original):
        remove_unwanted(document)
        user = get_user()
        lock_user = original.get('lock_user', None)
        force_unlock = document.get('force_unlock', False)
        user_id = str(user.get('_id'))
        if lock_user and str(lock_user) != user_id and not force_unlock:
            raise SuperdeskApiError.forbiddenError('The item was locked by another user')
        document['versioncreated'] = utcnow()
        set_item_expiry(document, original)
        document['version_creator'] = user_id
        if force_unlock:
            del document['force_unlock']

    def on_replaced(self, document, original):
        get_component(ItemAutosave).clear(original['_id'])
        add_activity(ACTIVITY_UPDATE, 'replaced item {{ type }} about {{ subject }}',
                     self.datasource, item=original,
                     type=original['type'], subject=get_subject(original))
        user = get_user()
        push_notification('item:replaced', item=str(original['_id']), user=str(user.get('_id')))

    def on_delete(self, doc):
        """Delete associated binary files."""
        if doc and doc.get('renditions'):
            for file_id in [rend.get('media') for rend in doc.get('renditions', {}).values()
                            if rend.get('media')]:
                try:
                    app.media.delete(file_id)
                except (NotFound):
                    pass

    def on_deleted(self, doc):
        if doc['type'] == 'composite':
            self.packageService.on_deleted(doc)
        add_activity(ACTIVITY_DELETE, 'removed item {{ type }} about {{ subject }}',
                     self.datasource, item=doc,
                     type=doc['type'], subject=get_subject(doc))
        user = get_user()
        push_notification('item:deleted', item=str(doc['_id']), user=str(user.get('_id')))

    def replace(self, id, document, original):
        return self.restore_version(id, document, original) or super().replace(id, document, original)

    def find_one(self, req, **lookup):
        item = super().find_one(req, **lookup)
        if item and str(item.get('task', {}).get('stage', '')) in \
                get_resource_service('users').get_invisible_stages_ids(get_user().get('_id')):
            raise SuperdeskApiError.forbiddenError("User does not have permissions to read the item.")
        return item

    def restore_version(self, id, doc, original):
        item_id = id
        old_version = int(doc.get('old_version', 0))
        last_version = int(doc.get('last_version', 0))
        if (not all([item_id, old_version, last_version])):
            return None

        old = get_resource_service('archive_versions').find_one(req=None, _id_document=item_id, _version=old_version)
        if old is None:
            raise SuperdeskApiError.notFoundError('Invalid version %s' % old_version)

        curr = get_resource_service(SOURCE).find_one(req=None, _id=item_id)
        if curr is None:
            raise SuperdeskApiError.notFoundError('Invalid item id %s' % item_id)

        if curr[config.VERSION] != last_version:
            raise SuperdeskApiError.preconditionFailedError('Invalid last version %s' % last_version)
        old['_id'] = old['_id_document']
        old['_updated'] = old['versioncreated'] = utcnow()
        set_item_expiry(old, doc)
        del old['_id_document']

        resolve_document_version(old, 'archive', 'PATCH', curr)

        remove_unwanted(old)
        super().replace(id=item_id, document=old, original=curr)

        del doc['old_version']
        del doc['last_version']
        doc.update(old)
        return item_id

    def duplicate_content(self, original_doc):
        if original_doc.get('type', '') == 'composite':
            for groups in original_doc.get('groups'):
                if groups.get('id') != 'root':
                    associations = groups.get('refs', [])
                    for assoc in associations:
                        if assoc.get('residRef'):
                            item, item_id, endpoint = self.packageService.get_associated_item(assoc)
                            assoc['residRef'] = assoc['guid'] = self.duplicate_content(item)

        return self.duplicate_item(original_doc)

    def duplicate_item(self, original_doc):
        new_doc = original_doc.copy()
        del new_doc['_id']
        del new_doc['guid']
        generate_unique_id_and_name(new_doc)
        item_model = get_model(ItemModel)
        on_duplicate_item(new_doc)
        item_model.create([new_doc])
        self.duplicate_versions(original_doc['guid'], new_doc)
        if new_doc.get('state') != 'submitted':
            get_resource_service('tasks').patch(new_doc['_id'], {'state': 'submitted'})
        return new_doc['guid']

    def duplicate_versions(self, old_id, new_doc):
        lookup = {'guid': old_id}
        old_versions = get_resource_service('archive_versions').get(req=None, lookup=lookup)

        new_versions = []
        for old_version in old_versions:
            old_version['_id_document'] = new_doc['_id']
            del old_version['_id']
            old_version['guid'] = new_doc['guid']
            old_version['unique_name'] = new_doc['unique_name']
            old_version['unique_id'] = new_doc['unique_id']
            old_version['versioncreated'] = utcnow()
            new_versions.append(old_version)
        if new_versions:
            get_resource_service('archive_versions').post(new_versions)

    def can_edit(self, item, user_id):
        """
        Determines if the user can edit the item or not.
        """
        # TODO: modify this function when read only permissions for stages are implemented
        # TODO: and Content state related checking.

        if not current_user_has_privilege('archive'):
            return False, 'User does not have sufficient permissions.'

        item_location = item.get('task')

        if item_location:
            if item_location.get('desk'):
                if not superdesk.get_resource_service('user_desks').is_member(user_id, item_location.get('desk')):
                    return False, 'User is not a member of the desk.'
            elif item_location.get('user'):
                if not str(item_location.get('user')) == str(user_id):
                    return False, 'Item belongs to another user.'

        return True, ''

    def __is_req_for_save(self, doc):
        """
        Patch of /api/archive is being used in multiple places. This method differentiates from the patch
        triggered by user or not.
        """

        if 'req_for_save' in doc:
            req_for_save = doc['req_for_save']
            del doc['req_for_save']

            return req_for_save == 'true'

        return True


class AutoSaveResource(Resource):
    endpoint_name = 'archive_autosave'
    item_url = item_url
    schema = {
        '_id': {'type': 'string'}
    }
    schema.update(metadata_schema)
    resource_methods = ['POST']
    item_methods = ['GET', 'PUT', 'PATCH']
    resource_title = endpoint_name
    privileges = {'POST': 'archive', 'PATCH': 'archive', 'PUT': 'archive'}


class ArchiveSaveService(BaseService):
    def create(self, docs, **kwargs):
        if not docs:
            raise SuperdeskApiError.notFoundError('Content is missing')
        req = parse_request(self.datasource)
        try:
            get_component(ItemAutosave).autosave(docs[0]['_id'], docs[0], get_user(required=True), req.if_match)
        except InvalidEtag:
            raise SuperdeskApiError.preconditionFailedError('Client and server etags don\'t match')
        return [docs[0]['_id']]

superdesk.workflow_state('in_progress')
superdesk.workflow_action(
    name='save',
    include_states=['draft', 'fetched', 'routed', 'submitted'],
    privileges=['archive']
)

superdesk.workflow_state('submitted')
superdesk.workflow_action(
    name='move',
    exclude_states=['ingested', 'spiked', 'on-hold', 'published', 'killed'],
    privileges=['archive']
)
