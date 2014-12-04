"""
Created on May 23, 2014

@author: Ioan v. Pocol
"""

import traceback

from celery.canvas import chord
from celery.result import AsyncResult
from eve.versioning import insert_versioning_documents
import flask
from flask.globals import current_app as app
from celery.exceptions import Ignore
from celery import states
from celery.utils.log import get_task_logger

import superdesk
from superdesk.utc import utc, utcnow
from superdesk.celery_app import celery, finish_task_for_progress,\
    finish_subtask_from_progress, add_subtask_to_progress
from superdesk.upload import url_for_media
from superdesk.media.media_operations import download_file_from_url, process_file
from superdesk.resource import Resource
from .common import get_user, aggregations
from superdesk.services import BaseService
from .archive import SOURCE as ARCHIVE


logger = get_task_logger(__name__)


def update_status(task_id, current, total):
    if current is None:
        current = 0
    archive_item.update_state(task_id, state='PROGRESS', meta={'current': int(current), 'total': int(total)})


def raise_fail(task_id, message):
    archive_item.update_state(task_id, state=states.FAILURE, meta={'error': message})
    # by raising Ignore the processing will stop(no retries) and the result is not updated anymore
    raise Ignore()


def import_rendition(guid, rendition_name, href, extract_metadata):
    archive = superdesk.get_resource_service(ARCHIVE).find_one(req=None, guid=guid)
    if not archive:
        msg = 'No document found in the media archive with this ID: %s' % guid
        raise superdesk.SuperdeskError(payload=msg)

    if rendition_name not in archive['renditions']:
        payload = 'Invalid rendition name %s' % rendition_name
        raise superdesk.SuperdeskError(payload=payload)

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


def remove_unwanted(doc):
    """
    As the name suggests this function removes unwanted attributes from doc to make an entry in Mongo and Elastic.
    """

    if '_type' in doc:
        del doc['_type']


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

        '''
        Necessary because flask.g.user is None while fetching packages the for grouped items or
        while patching in archive collection. Without this version_creator is set None which doesn't make sense.
        '''
        flask.g.user = user
        remove_unwanted(item)
        superdesk.get_resource_service(ARCHIVE).patch(guid, item)

        tasks = []
        for group in item.get('groups', []):
            for ref in group.get('refs', []):
                if 'residRef' in ref:
                    resid_ref = ref.get('residRef')
                    doc = {'guid': resid_ref, 'ingest_provider': provider_id, 'task_id': crt_task_id}

                    archived_doc = superdesk.get_resource_service(ARCHIVE).find_one(req=None, guid=doc.get('guid'))
                    # check if task already started
                    if not archived_doc:
                        doc.setdefault('_id', doc.get('guid'))
                        superdesk.get_resource_service(ARCHIVE).post([doc])
                    elif archived_doc.get('task_id') == crt_task_id:
                        # it is a retry so continue
                        archived_doc.update(doc)
                        remove_unwanted(archived_doc)
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


def insert_into_versions(guid, task_id):
    """
    Since the request is handled by Celery we need to manually persist the initial version into versions collection.
    If the ingest content is of type composite/package then archive_item creates sub-tasks
    """

    archived_doc = superdesk.get_resource_service(ARCHIVE).find_one(req=None, _id=guid)
    remove_unwanted(archived_doc)

    if 'task_id' not in archived_doc:
        updates = superdesk.get_resource_service(ARCHIVE).patch(guid, {"task_id": task_id})
        archived_doc.update(updates)

    if app.config['VERSION'] in archived_doc:
        insert_versioning_documents(ARCHIVE, archived_doc)


def mark_ingest_as_archived(guid=None, ingest_doc=None):
    """
    Updates the ingest document as archived. If guid is not None then first searches the collection for the document
    and if found updates the same as archived.
    """

    if guid is not None:
        ingest_doc = superdesk.get_resource_service('ingest').find_one(req=None, _id=guid)

    if ingest_doc:
        superdesk.get_resource_service('ingest').patch(ingest_doc.get('_id'), {'archived': utcnow()})


class ArchiveIngestResource(Resource):
    resource_methods = ['POST']
    item_methods = ['GET']
    datasource = {
        'search_backend': 'elastic',
        'aggregations': aggregations,
    }
    additional_lookup = {
        'url': 'regex("[\w-]+")',
        'field': 'task_id'
    }
    schema = {
        'guid': {
            'type': 'string',
            'required': True,
        },
        'task_id': {
            'type': 'string',
            'required': False,
        }
    }
    privileges = {'POST': 'ingest_move'}


class ArchiveIngestService(BaseService):

    def _copy_from_ingest_doc(self, doc, ingest_doc):
        """
        As the name suggests this method copies some of the values from ingest_doc.
        """

        # doc.setdefault('user', str(getattr(flask.g, 'user', {}).get('_id')))
        doc.setdefault('_id', doc.get('guid'))
        doc.setdefault('unique_id', ingest_doc.get('unique_id'))
        doc.setdefault('unique_name', ingest_doc.get('unique_name'))
        doc.setdefault('type', ingest_doc['type'] if 'type' in ingest_doc else '')

    def create(self, docs, **kwargs):
        for doc in docs:
            ingest_doc = superdesk.get_resource_service('ingest').find_one(req=None, _id=doc.get('guid'))
            if not ingest_doc:
                msg = 'Fail to found ingest item with guid: %s' % doc.get('guid')
                raise superdesk.SuperdeskError(payload=msg)

            mark_ingest_as_archived(ingest_doc=ingest_doc)

            archived_doc = superdesk.get_resource_service(ARCHIVE).find_one(req=None, guid=doc.get('guid'))
            if not archived_doc:
                self._copy_from_ingest_doc(doc, ingest_doc)
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
            raise superdesk.SuperdeskError(payload=msg)
