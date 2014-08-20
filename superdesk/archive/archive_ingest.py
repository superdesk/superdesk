'''
Created on May 23, 2014

@author: Ioan v. Pocol
'''

from celery.canvas import chord
import flask

import superdesk
from superdesk.io import providers

from superdesk.utc import utc, utcnow
from superdesk.celery_app import celery, finish_task_for_progress,\
    finish_subtask_from_progress, add_subtask_to_progress
from celery.result import AsyncResult
from flask.globals import current_app as app
from superdesk.upload import url_for_media
from superdesk.media.media_operations import download_file_from_url,\
    process_file
from superdesk.base_model import BaseModel
from celery.exceptions import Ignore
from celery import states
from superdesk.archive.common import facets
import traceback
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


def update_status(task_id, current, total):
    if current is None:
        current = 0
    archive_item.update_state(task_id, state='PROGRESS', meta={'current': int(current), 'total': int(total)})


def raise_fail(task_id, message):
    archive_item.update_state(task_id, state=states.FAILURE, meta={'error': message})
    # by raising Ignore the processing will stop(no retries) and the result is not updated anymore
    raise Ignore()


def import_rendition(guid, rendition_name, href, extract_metadata, trigger_events):
    archive = superdesk.apps['archive'].find_one(req=None, guid=guid)
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
    result = superdesk.apps['archive'].update(id=guid, updates=updates, trigger_events=trigger_events)

    return result


@celery.task(bind=True, max_retries=3)
def archive_media(self, task_id, guid, href, trigger_events):
    try:
        if not self.request.retries:
            update_status(*add_subtask_to_progress(task_id))
        import_rendition(guid, 'baseImage', href, True, trigger_events)
        update_status(*finish_subtask_from_progress(task_id))
    except Exception:
        raise self.retry(countdown=2)


@celery.task(bind=True, max_retries=3)
def archive_rendition(self, task_id, guid, name, href, trigger_events):
    try:
        if not self.request.retries:
            update_status(*add_subtask_to_progress(task_id))
        import_rendition(guid, name, href, False, trigger_events)
        update_status(*finish_subtask_from_progress(task_id))
    except Exception:
        raise self.retry(countdown=2)


@celery.task()
def update_item(result, is_main_task, task_id, guid):
    if is_main_task:
        update_status(*finish_task_for_progress(task_id))


@celery.task(bind=True, max_retries=3)
def archive_item(self, guid, provider_id, user, trigger_events, task_id=None, ):
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

        provider = superdesk.apps['ingest_providers'].find_one(req=None, _id=provider_id)
        if provider is None:
            message = 'For ingest with guid= %s, failed to retrieve provider with _id=%s' % (guid, provider_id)
            raise_fail(task_id, message)
        service_provider = providers[provider.get('type')]
        service_provider.provider = provider

        item = None
        old_item = False
        try:
            items = service_provider.get_items(guid)
        except LookupError:
            ingest_doc = superdesk.apps['ingest'].find_one(req=None, _id=guid)
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
        superdesk.apps['archive'].update(guid, item, trigger_events=trigger_events)

        tasks = []
        for group in item.get('groups', []):
            for ref in group.get('refs', []):
                if 'residRef' in ref:
                    doc = {'guid': ref.get('residRef'), 'ingest_provider': provider_id,
                           'user': user, 'task_id': crt_task_id}

                    archived_doc = superdesk.apps['archive'].find_one(req=None, guid=doc.get('guid'))
                    # check if task already started
                    if not archived_doc:
                        doc.setdefault('_id', doc.get('guid'))
                        superdesk.apps['archive'].create([doc], trigger_events=trigger_events)
                    elif archived_doc.get('task_id') == crt_task_id:
                        # it is a retry so continue
                        archived_doc.update(doc)
                        superdesk.apps['archive'].update(archived_doc.get('_id'), archived_doc,
                                                         trigger_events=trigger_events)
                    else:
                        # there is a cyclic dependency, skip it
                        continue

                    ingest_set_archived(doc.get('guid'))
                    tasks.append(archive_item.s(ref['residRef'], provider.get('_id'), user, trigger_events, task_id))

        for rendition in item.get('renditions', {}).values():
            href = service_provider.prepare_href(rendition['href'])
            if rendition['rendition'] == 'baseImage':
                tasks.append(archive_media.s(task_id, guid, href, trigger_events))
            else:
                tasks.append(archive_rendition.s(task_id, guid, rendition['rendition'], href, trigger_events))

        update_status(*finish_subtask_from_progress(task_id))
        if tasks:
            chord((task for task in tasks), update_item.s(crt_task_id == task_id, task_id, guid)).delay()
        elif task_id == crt_task_id:
            update_status(*finish_task_for_progress(task_id))
    except Exception:
        logger.error(traceback.format_exc())


def ingest_set_archived(guid):
    ingest_doc = superdesk.apps['ingest'].find_one(req=None, _id=guid)
    if ingest_doc:
        superdesk.apps['ingest'].update(ingest_doc.get('_id'), {'archived': utcnow()}, trigger_events=True)


class ArchiveIngestModel(BaseModel):
    endpoint_name = 'archive_ingest'
    resource_methods = ['POST']
    item_methods = ['GET']
    datasource = {
        'search_backend': 'elastic',
        'facets': facets
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

    def create(self, docs, trigger_events=None, **kwargs):
        for doc in docs:
            ingest_doc = superdesk.apps['ingest'].find_one(req=None, _id=doc.get('guid'))
            if not ingest_doc:
                msg = 'Fail to found ingest item with guid: %s' % doc.get('guid')
                raise superdesk.SuperdeskError(payload=msg)
            ingest_set_archived(doc.get('guid'))

            archived_doc = superdesk.apps['archive'].find_one(req=None, guid=doc.get('guid'))
            if not archived_doc:
                doc.setdefault('_id', doc.get('guid'))
                doc.setdefault('user', str(getattr(flask.g, 'user', {}).get('_id')))
                superdesk.apps['archive'].create([doc], trigger_events=trigger_events)

            task = archive_item.delay(doc.get('guid'), ingest_doc.get('ingest_provider'),
                                      doc.get('user'), trigger_events)
            doc['task_id'] = task.id
            if task.state not in ('PROGRESS', states.SUCCESS, states.FAILURE) and not task.result:
                update_status(task.id, 0, 0)

            superdesk.apps['archive'].update(doc.get('guid'), {"task_id": task.id}, trigger_events=trigger_events)

        return [doc.get('guid') for doc in docs]

    def update(self, id, updates, trigger_events=None):
        pass

    def delete(self, lookup, trigger_events=None):
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
