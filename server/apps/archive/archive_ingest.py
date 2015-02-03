# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""
Created on May 23, 2014

@author: Ioan v. Pocol
"""

import flask
import traceback
import superdesk

from celery.canvas import chord
from celery.result import AsyncResult
from eve.utils import config
from flask.globals import current_app as app
from celery.exceptions import Ignore
from celery import states
from celery.utils.log import get_task_logger
from apps.archive.common import insert_into_versions, remove_unwanted, set_original_creator
from apps.tasks import send_to

import superdesk
from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from superdesk.utc import utc, utcnow
from superdesk.celery_app import celery, finish_task_for_progress,\
    finish_subtask_from_progress, add_subtask_to_progress
from superdesk.upload import url_for_media
from superdesk.media.media_operations import download_file_from_url, process_file
from superdesk.resource import Resource
from .common import get_user
from superdesk.services import BaseService
from .archive import SOURCE as ARCHIVE
from superdesk.workflow import is_workflow_state_transition_valid
from superdesk.notification import push_notification


STATE_FETCHED = 'fetched'


logger = get_task_logger(__name__)


def update_status(task_id, current, total):
    if current is None:
        current = 0
    progress = {'current': int(current), 'total': int(total)}
    archive_item.update_state(task_id, state='PROGRESS', meta=progress)
    push_notification('task:progress', task=task_id, progress=progress)


def raise_fail(task_id, message):
    archive_item.update_state(task_id, state=states.FAILURE, meta={'error': message})
    # by raising Ignore the processing will stop(no retries) and the result is not updated anymore
    raise Ignore()


def import_rendition(guid, rendition_name, href, extract_metadata):
    archive = superdesk.get_resource_service(ARCHIVE).find_one(req=None, guid=guid)
    if not archive:
        msg = 'No document found in the media archive with this ID: %s' % guid
        raise SuperdeskApiError.notFoundError(msg)

    if rendition_name not in archive['renditions']:
        payload = 'Invalid rendition name %s' % rendition_name
        raise SuperdeskApiError.notFoundError(payload)

    updates = {}
    metadata = None

    content, filename, content_type = download_file_from_url(href)
    if extract_metadata:
        file_type, ext = content_type.split('/')
        metadata = process_file(content, file_type)

    file_guid = app.media.put(content, filename, content_type, metadata)

    # perform partial update
    updates['renditions.' + rendition_name + '.href'] = url_for_media(file_guid)
    updates['renditions.' + rendition_name + '.media'] = file_guid
    updates['req_for_save'] = 'false'
    result = superdesk.get_resource_service(ARCHIVE).patch(guid, updates=updates)

    return result


@celery.task(bind=True, max_retries=3)
def archive_media(self, task_id, guid, href):
    try:
        if not self.request.retries:
            update_status(*add_subtask_to_progress(task_id))
        import_rendition(guid, 'baseImage', href, True)
        update_status(*finish_subtask_from_progress(task_id))
    except Exception:
        raise self.retry(countdown=2)


@celery.task(bind=True, max_retries=3)
def archive_rendition(self, task_id, guid, name, href):
    try:
        if not self.request.retries:
            update_status(*add_subtask_to_progress(task_id))
        import_rendition(guid, name, href, False)
        update_status(*finish_subtask_from_progress(task_id))
    except Exception:
        raise self.retry(countdown=2)


@celery.task()
def update_item(result, is_main_task, task_id, guid):
    insert_into_versions(guid, task_id)
    if is_main_task:
        update_status(*finish_task_for_progress(task_id))


def _update_archive(guid, item):
    """
    Assigns a State to the content, removes unwanted attributes, sets the original creator and updates the item in
    archive collection.

    :param guid:
    :param item: from ingest collection
    """

    item[config.CONTENT_STATE] = STATE_FETCHED
    remove_unwanted(item)
    set_original_creator(item)
    superdesk.get_resource_service(ARCHIVE).update(guid, item)


@celery.task(bind=True, max_retries=3)
def archive_item(self, guid, provider_id, user, task_id=None):
    try:
        # For CELERY_ALWAYS_EAGER=True the current request context is
        # empty but already initialized one is on request_stack
        if app.config['CELERY_ALWAYS_EAGER']:
            self.request_stack.pop()

        crt_task_id = self.request.id
        if not task_id:
            task_id = crt_task_id

        if not self.request.retries:
            update_status(*add_subtask_to_progress(task_id))

        provider = superdesk.get_resource_service('ingest_providers').find_one(req=None, _id=provider_id)
        if provider is None:
            message = 'For ingest with guid= %s, failed to retrieve provider with _id=%s' % (guid, provider_id)
            raise_fail(task_id, message)
        service_provider = superdesk.io.providers[provider.get('type')]
        service_provider.provider = provider

        item = None
        old_item = False
        try:
            items = service_provider.get_items(guid)
        except LookupError:
            ingest_doc = superdesk.get_resource_service('ingest').find_one(req=None, _id=guid)
            if not ingest_doc:
                message = 'Not found the ingest with guid: %s for provider %s' % (guid, provider.get('type'))
                raise_fail(task_id, message)
            else:
                old_item = True
                ingest_doc.pop('_id')
                items = [ingest_doc]
        except Exception:
            raise self.retry(countdown=2)

        for item_it in items:
            if 'guid' in item_it and item_it['guid'] == guid:
                item = item_it
                break

        if item is None:
            message = 'Returned ingest but not found the ingest with guid: %s for provider %s' \
                      % (guid, provider.get('type'))
            raise_fail(task_id, message)

        if not old_item:
            item['created'] = item['firstcreated'] = utc.localize(item['firstcreated'])
            item['updated'] = item['versioncreated'] = utc.localize(item['versioncreated'])

        # Necessary because flask.g.user is None while fetching packages the for grouped items or
        # while patching in archive collection. Without this version_creator is set None which doesn't make sense.
        flask.g.user = user
        _update_archive(guid, item)

        tasks = []
        for group in item.get('groups', []):
            for ref in group.get('refs', []):
                if 'residRef' in ref:
                    resid_ref = ref.get('residRef')
                    doc = {'guid': resid_ref, 'ingest_provider': provider_id, 'task_id': crt_task_id}
                    archived_doc = superdesk.get_resource_service(ARCHIVE).find_one(req=None, guid=resid_ref)

                    if not archived_doc:  # Check if task already started
                        '''
                        We need to fetch the sub-documents from DB. Otherwise metadata attributes like unique_id,
                        unique_name, state, type will be re-defined rather than copying from ingest doc.
                        '''
                        resid_ref_doc = superdesk.get_resource_service('ingest').find_one(req=None, guid=resid_ref)
                        create_from_ingest_doc(doc, resid_ref_doc)

                        superdesk.get_resource_service(ARCHIVE).post([doc])
                    elif archived_doc.get('task_id') == crt_task_id:
                        # it is a retry so continue
                        archived_doc.update(doc)
                        archived_doc['req_for_save'] = 'false'
                        superdesk.get_resource_service(ARCHIVE).patch(archived_doc.get('_id'), archived_doc)
                    else:
                        # there is a cyclic dependency, skip it
                        continue

                    mark_ingest_as_archived(doc.get('guid'))
                    tasks.append(archive_item.s(resid_ref, provider.get('_id'), user, task_id))

        for rendition in item.get('renditions', {}).values():
            href = service_provider.prepare_href(rendition['href'])
            if rendition['rendition'] == 'baseImage':
                tasks.append(archive_media.s(task_id, guid, href))
            else:
                tasks.append(archive_rendition.s(task_id, guid, rendition['rendition'], href))

        update_status(*finish_subtask_from_progress(task_id))
        if tasks:
            chord((task for task in tasks), update_item.s(crt_task_id == task_id, task_id, guid)).delay()
        else:
            insert_into_versions(guid, task_id)
            if task_id == crt_task_id:
                update_status(*finish_task_for_progress(task_id))
    except Exception:
        logger.error(traceback.format_exc())


def mark_ingest_as_archived(guid=None, ingest_doc=None):
    """
    Updates the ingest document as archived. If guid is not None then first searches the collection for the document
    and if found updates the same as archived.
    """

    if guid is not None:
        ingest_doc = superdesk.get_resource_service('ingest').find_one(req=None, _id=guid)

    if ingest_doc:
        superdesk.get_resource_service('ingest').patch(ingest_doc.get('_id'), {'archived': utcnow()})


def create_from_ingest_doc(dest_doc, source_doc):
    """Create a new archive item using values from given source doc.

    :param dest_doc: doc which gets persisted into archive collection
    :param source_doc: doc which is fetched from ingest collection
    """
    for key, val in source_doc.items():
        dest_doc.setdefault(key, val)

    dest_doc[config.VERSION] = 1
    dest_doc[config.CONTENT_STATE] = STATE_FETCHED


class ArchiveIngestResource(Resource):
    resource_methods = ['POST']
    item_methods = ['GET']
    additional_lookup = {
        'url': 'regex("[\w-]+")',
        'field': 'task_id'
    }
    schema = {
        'guid': {'type': 'string', 'required': True},
        'desk': Resource.rel('desks', False, nullable=True),
        'task_id': {'type': 'string', 'required': False},
    }
    privileges = {'POST': 'ingest_move'}


class ArchiveIngestService(BaseService):

    def create(self, docs, **kwargs):
        for doc in docs:
            ingest_doc = superdesk.get_resource_service('ingest').find_one(req=None, _id=doc.get('guid'))
            if not ingest_doc:
                msg = 'Fail to found ingest item with guid: %s' % doc.get('guid')
                raise SuperdeskApiError.notFoundError(msg)

            if not is_workflow_state_transition_valid('fetch_as_from_ingest', ingest_doc[config.CONTENT_STATE]):
                raise InvalidStateTransitionError()

            mark_ingest_as_archived(ingest_doc=ingest_doc)

            archived_doc = superdesk.get_resource_service(ARCHIVE).find_one(req=None, _id=doc.get('guid'))
            if not archived_doc:
                create_from_ingest_doc(doc, ingest_doc)
                send_to(doc, doc.get('desk'))
                superdesk.get_resource_service(ARCHIVE).post([doc])

            task = archive_item.delay(doc.get('guid'), ingest_doc.get('ingest_provider'), get_user())

            doc['task_id'] = task.id
            if task.state not in ('PROGRESS', states.SUCCESS, states.FAILURE) and not task.result:
                update_status(task.id, 0, 0)

        return [doc.get('guid') for doc in docs]

    def update(self, id, updates):
        pass

    def delete(self, lookup):
        pass

    def find_one(self, req=None, **lookup):
        try:
            task_id = lookup["task_id"]
            task = AsyncResult(task_id)

            if task.state in ('PROGRESS', states.SUCCESS, states.FAILURE) and task.result:
                doc = task.result
            else:
                doc = {}

            doc['state'] = task.state
            doc['task_id'] = task_id
            doc['_id'] = task_id
            doc['_created'] = doc['_updated'] = utcnow()

            return doc
        except Exception:
            msg = 'No progress information is available for task_id: %s' % task_id
            raise SuperdeskApiError.notFoundError(msg)


superdesk.workflow_state(STATE_FETCHED)

superdesk.workflow_action(
    name='fetch_as_from_ingest',
    include_states=['ingested'],
    privileges=['archive', 'ingest_move']
)

superdesk.workflow_state('routed')
superdesk.workflow_action(
    name='route',
    include_states=['ingested']
)
