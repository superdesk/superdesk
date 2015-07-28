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
from settings import DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES, VERSION

SOURCE = 'archive'

import flask
from superdesk.resource import Resource
from .common import extra_response_fields, item_url, aggregations, remove_unwanted, update_state, set_item_expiry, \
    is_update_allowed
from .common import on_create_item, on_duplicate_item
from .common import get_user, update_version, set_sign_off, handle_existing_data, item_schema
from flask import current_app as app
from werkzeug.exceptions import NotFound
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from eve.versioning import resolve_document_version, versioned_id_field
from superdesk.activity import add_activity, ACTIVITY_CREATE, ACTIVITY_UPDATE, ACTIVITY_DELETE
from eve.utils import parse_request, config
from superdesk.services import BaseService
from apps.users.services import is_admin
from apps.content import metadata_schema
from apps.common.components.utils import get_component
from apps.item_autosave.components.item_autosave import ItemAutosave
from apps.common.models.base_model import InvalidEtag
from superdesk.etree import get_word_count
from superdesk.notification import push_notification
from copy import copy, deepcopy
import superdesk
import logging
from apps.common.models.utils import get_model
from apps.item_lock.models.item import ItemModel
from apps.packages import PackageService, TakesPackageService
from .archive_media import ArchiveMediaService
from superdesk.utc import utcnow
import datetime
from apps.archive.common import ITEM_DUPLICATE, ITEM_OPERATION, ITEM_RESTORE,\
    ITEM_UPDATE, ITEM_DESCHEDULE


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
    schema = item_schema()
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
        'elastic_filter': {'terms': {'state': ['fetched', 'routed', 'draft', 'in_progress', 'spiked', 'submitted']}},
        'elastic_filter_callback': private_content_filter
    }
    etag_ignore_fields = ['highlights']
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
    takesService = TakesPackageService()
    mediaService = ArchiveMediaService()

    def on_fetched(self, docs):
        """
        Overriding this to handle existing data in Mongo & Elastic
        """
        self.__enhance_items(docs[config.ITEMS])

    def on_fetched_item(self, doc):
        self.__enhance_items([doc])

    def __enhance_items(self, items):
        for item in items:
            handle_existing_data(item)
            self.takesService.enhance_with_package_info(item)

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

            # let client create version 0 docs
            if doc.get('version') == 0:
                doc[config.VERSION] = doc['version']

            if not doc.get('ingest_provider'):
                doc['source'] = DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES

    def on_created(self, docs):
        packages = [doc for doc in docs if doc['type'] == 'composite']
        if packages:
            self.packageService.on_created(packages)

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
        updates[ITEM_OPERATION] = ITEM_UPDATE
        is_update_allowed(original)
        user = get_user()

        if 'publish_schedule' in updates and original['state'] == 'scheduled':
            # this is an deschedule action
            self.deschedule_item(updates, original)
            # check if there is a takes package and deschedule the takes package.
            package = TakesPackageService().get_take_package(original)
            if package and package.get('state') == 'scheduled':
                package_updates = {'publish_schedule': None, 'groups': package.get('groups')}
                self.patch(package.get(config.ID_FIELD), package_updates)
            return

        if updates.get('publish_schedule'):
            if datetime.datetime.fromtimestamp(False).date() == updates.get('publish_schedule').date():
                # publish_schedule field will be cleared
                updates['publish_schedule'] = None
            else:
                # validate the schedule
                self.validate_schedule(updates.get('publish_schedule'))

        if 'unique_name' in updates and not is_admin(user) \
                and (user['active_privileges'].get('metadata_uniquename', 0) == 0):
            raise SuperdeskApiError.forbiddenError("Unauthorized to modify Unique Name")

        remove_unwanted(updates)

        if self.__is_req_for_save(updates):
            update_state(original, updates)

        lock_user = original.get('lock_user', None)
        force_unlock = updates.get('force_unlock', False)

        updates.setdefault('original_creator', original.get('original_creator'))

        str_user_id = str(user.get('_id')) if user else None
        if lock_user and str(lock_user) != str_user_id and not force_unlock:
            raise SuperdeskApiError.forbiddenError('The item was locked by another user')

        updates['versioncreated'] = utcnow()
        set_item_expiry(updates, original)
        updates['version_creator'] = str_user_id
        set_sign_off(updates, original)
        update_word_count(updates)

        if force_unlock:
            del updates['force_unlock']

        if original['type'] == 'composite':
            self.packageService.on_update(updates, original)

        update_version(updates, original)

    def on_updated(self, updates, original):
        get_component(ItemAutosave).clear(original['_id'])

        if original['type'] == 'composite':
            self.packageService.on_updated(updates, original)

        user = get_user()

        if config.VERSION in updates:
            updated = copy(original)
            updated.update(updates)
            add_activity(ACTIVITY_UPDATE, 'created new version {{ version }} for item {{ type }} about "{{ subject }}"',
                         self.datasource, item=updated,
                         version=updates[config.VERSION], subject=get_subject(updates, original),
                         type=updated['type'])

        push_notification('item:updated', item=str(original['_id']), user=str(user.get('_id')))

    def on_replace(self, document, original):
        document[ITEM_OPERATION] = ITEM_UPDATE
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

        handle_existing_data(item)
        return item

    def restore_version(self, id, doc, original):
        item_id = id
        old_version = int(doc.get('old_version', 0))
        last_version = int(doc.get('last_version', 0))
        if (not all([item_id, old_version, last_version])):
            return None

        old = get_resource_service('archive_versions').find_one(req=None, _id_document=item_id,
                                                                _current_version=old_version)
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
        old[ITEM_OPERATION] = ITEM_RESTORE

        resolve_document_version(old, 'archive', 'PATCH', curr)

        remove_unwanted(old)
        super().replace(id=item_id, document=old, original=curr)

        del doc['old_version']
        del doc['last_version']
        doc.update(old)
        return item_id

    def duplicate_content(self, original_doc):
        """
        Duplicates the 'original_doc' including it's version history. Copy and Duplicate actions use this method.

        :return: guid of the duplicated article
        """

        if original_doc.get('type', '') == 'composite':
            for groups in original_doc.get('groups'):
                if groups.get('id') != 'root':
                    associations = groups.get('refs', [])
                    for assoc in associations:
                        if assoc.get('residRef'):
                            item, _item_id, _endpoint = self.packageService.get_associated_item(assoc)
                            assoc['residRef'] = assoc['guid'] = self.duplicate_content(item)

        return self._duplicate_item(original_doc)

    def _duplicate_item(self, original_doc):
        """
        Duplicates the 'original_doc' including it's version history. If the article being duplicated is contained
        in a desk then the article state is changed to Submitted.

        :return: guid of the duplicated article
        """

        new_doc = original_doc.copy()
        del new_doc[config.ID_FIELD]
        del new_doc['guid']

        new_doc[ITEM_OPERATION] = ITEM_DUPLICATE
        item_model = get_model(ItemModel)

        on_duplicate_item(new_doc)
        resolve_document_version(new_doc, 'archive', 'PATCH', new_doc)
        if original_doc.get('task', {}).get('desk') is not None and new_doc.get('state') != 'submitted':
            new_doc[config.CONTENT_STATE] = 'submitted'
        item_model.create([new_doc])
        self._duplicate_versions(original_doc['guid'], new_doc)

        return new_doc['guid']

    def _duplicate_versions(self, old_id, new_doc):
        """
        Duplicates the version history of the article identified by old_id. Each version identifiers are changed
        to have the identifiers of new_doc.

        :param old_id: identifier to fetch version history
        :param new_doc: identifiers from this doc will be used to create version history for the duplicated item.
        """

        old_versions = get_resource_service('archive_versions').get(req=None, lookup={'guid': old_id})

        new_versions = []
        for old_version in old_versions:
            old_version[versioned_id_field()] = new_doc[config.ID_FIELD]
            del old_version[config.ID_FIELD]

            old_version['guid'] = new_doc['guid']
            old_version['unique_name'] = new_doc['unique_name']
            old_version['unique_id'] = new_doc['unique_id']
            old_version['versioncreated'] = utcnow()
            if old_version[VERSION] == new_doc[VERSION]:
                old_version[ITEM_OPERATION] = new_doc[ITEM_OPERATION]
            new_versions.append(old_version)
        last_version = deepcopy(new_doc)
        last_version['_id_document'] = new_doc['_id']
        del last_version['_id']
        new_versions.append(last_version)
        if new_versions:
            get_resource_service('archive_versions').post(new_versions)

    def deschedule_item(self, updates, doc):
        """
        Deschedule an item. This operation removed the item from publish queue and published collection.
        :param dict updates: updates for the document
        :param doc: original is document.
        """
        updates['state'] = 'in_progress'
        updates['publish_schedule'] = None
        updates[ITEM_OPERATION] = ITEM_DESCHEDULE
        # delete entries from publish queue
        get_resource_service('publish_queue').delete_by_article_id(doc['_id'])
        # delete entry from published repo
        get_resource_service('published').delete_by_article_id(doc['_id'])

    def validate_schedule(self, schedule):
        if not isinstance(schedule, datetime.date):
            raise SuperdeskApiError.badRequestError("Schedule date is not recognized")
        if not schedule.date() or schedule.date().year <= 1970:
            raise SuperdeskApiError.badRequestError("Schedule date is not recognized")
        if not schedule.time():
            raise SuperdeskApiError.badRequestError("Schedule time is not recognized")
        if schedule < utcnow():
            raise SuperdeskApiError.badRequestError("Schedule cannot be earlier than now")

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

    def remove_expired(self, doc):
        """
        Removes the article from production if the state is spiked
        """

        assert doc[config.CONTENT_STATE] == 'spiked', \
            "Article state is %s. Only Spiked Articles can be removed" % doc[config.CONTENT_STATE]

        doc_id = str(doc[config.ID_FIELD])
        super().delete_action({config.ID_FIELD: doc_id})
        get_resource_service('archive_versions').delete(lookup={versioned_id_field(): doc_id})

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
    schema = item_schema({'_id': {'type': 'string'}})
    resource_methods = ['POST']
    item_methods = ['GET', 'PUT', 'PATCH', 'DELETE']
    resource_title = endpoint_name
    privileges = {'POST': 'archive', 'PATCH': 'archive', 'PUT': 'archive', 'DELETE': 'archive'}


class ArchiveSaveService(BaseService):
    def create(self, docs, **kwargs):
        if not docs:
            raise SuperdeskApiError.notFoundError('Content is missing')
        req = parse_request(self.datasource)
        try:
            get_component(ItemAutosave).autosave(docs[0]['_id'], docs[0], get_user(required=True), req.if_match)
        except InvalidEtag:
            raise SuperdeskApiError.preconditionFailedError('Client and server etags don\'t match')
        except KeyError:
            raise SuperdeskApiError.badRequestError("Request for Auto-save must have _id")
        return [docs[0]['_id']]


superdesk.workflow_state('in_progress')
superdesk.workflow_action(
    name='save',
    include_states=['draft', 'fetched', 'routed', 'submitted', 'scheduled'],
    privileges=['archive']
)

superdesk.workflow_state('submitted')
superdesk.workflow_action(
    name='move',
    exclude_states=['ingested', 'spiked', 'on-hold', 'published', 'scheduled', 'killed'],
    privileges=['archive']
)
