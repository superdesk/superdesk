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
from .common import ARCHIVE_MEDIA
from superdesk.upload import url_for_media
from superdesk.media_operations import store_file_from_url
from superdesk.base_model import BaseModel


def import_media(media_archive_guid, href):
    '''
    media_archive_guid: media_archive guid
    href: external file URL from which to download it
    Download from href and save file on app storage, process it and
    update "original" rendition for guid content item
    '''
    rv = import_rendition(media_archive_guid, 'baseImage', href)
    return rv


def import_rendition(media_archive_guid, rendition_name, href):
    '''
    media_archive_guid: media_archive guid
    rendition_name: rendition to update,
    href: external file URL from which to download it
    Download from href and save file on app storage, process it and
    update "rendition_name" rendition for guid content item
    '''
    archive = fetch_media_from_archive(media_archive_guid)
    if rendition_name not in archive['renditions']:
        payload = 'Invalid rendition name %s' % rendition_name
        raise superdesk.SuperdeskError(payload=payload)

    file_guid = store_file_from_url(href)
    updates = {}
    updates['renditions'] = {rendition_name: {'href': url_for_media(file_guid)}}
    rv = superdesk.apps[ARCHIVE_MEDIA].update(id=str(media_archive_guid), updates=updates,
                                              trigger_events=True)
    return rv


def fetch_media_from_archive(media_archive_guid):
    print('Fetching media from archive with id=', media_archive_guid)
    archive = superdesk.apps[ARCHIVE_MEDIA].find_one(req=None, _id=str(media_archive_guid))
    if not archive:
        msg = 'No document found in the media archive with this ID: %s' % media_archive_guid
        raise superdesk.SuperdeskError(payload=msg)
    return archive


def update_status(task_id, current, total):
    if current is None:
        current = 0
    archive_item.update_state(task_id, state='PROGRESS', meta={'current': int(current), 'total': int(total)})


@celery.task(bind=True, max_retries=3)
def archive_media(self, task_id, guid, href):
    try:
        if self.request.retries == 0:
            update_status(*add_subtask_to_progress(task_id))
        import_media(guid, href)
        update_status(*finish_subtask_from_progress(task_id))
    except Exception:
        raise self.retry(countdown=2)


@celery.task(bind=True, max_retries=3)
def archive_rendition(self, task_id, guid, name, href):
    try:
        if self.request.retries == 0:
            update_status(*add_subtask_to_progress(task_id))
        import_rendition(guid, name, href)
        update_status(*finish_subtask_from_progress(task_id))
    except Exception:
        raise self.retry(countdown=2)


@celery.task()
def update_item(result, is_main_task, task_id, guid):
    # update import status as done
    data = app.data
    data.update('archive', guid, {"task_id": ""})

    if is_main_task:
        update_status(*finish_task_for_progress(task_id))


@celery.task(bind=True, max_retries=3)
def archive_item(self, guid, provider_id, user, task_id=None):
    data = app.data

    crt_task_id = self.request.id
    if not task_id:
        task_id = crt_task_id

    if self.request.retries == 0:
        update_status(*add_subtask_to_progress(task_id))

    provider = data.find_one('ingest_providers', _id=provider_id, req=None)
    if provider is None:
        payload = 'For ingest with guid= %s, failed to retrieve provider with _id=%s' % (guid, provider_id)
        raise superdesk.SuperdeskError(payload=payload)
    service_provider = providers[provider.get('type')]
    service_provider.provider = provider

    item = None
    try:
        items = service_provider.get_items(guid)
    except Exception:
        raise self.retry(countdown=2)

    for item_it in items:
        if item_it['guid'] == guid:
            item = item_it
            break

    if item is None:
        payload = 'Not found the ingest with guid: %s for provider %s' % (guid, provider.get('type'))
        raise superdesk.SuperdeskError(payload=payload)

    item['created'] = item['firstcreated'] = utc.localize(item['firstcreated'])
    item['updated'] = item['versioncreated'] = utc.localize(item['versioncreated'])
    data.update('archive', guid, item)

    tasks = []

    for group in item.get('groups', []):
        for ref in group.get('refs', []):
            if 'residRef' in ref:
                doc = {'guid': ref.get('residRef'), 'ingest_provider': provider_id,
                       'user': user, 'task_id': crt_task_id}

                archived_doc = data.find_one('archive', guid=doc.get('guid'), req=None)
                # check if task already started
                if not archived_doc:
                    doc.setdefault('_id', doc.get('guid'))
                    data.insert('archive', [doc])
                elif archived_doc.get('task_id') == crt_task_id:
                    # it is a retry so continue
                    archived_doc.update(doc)
                    data.update('archive', archived_doc)
                else:
                    # there is a cyclic dependency, skip it
                    continue

                ingest_set_archived(doc.get('guid'))
                tasks.append(archive_item.s(task_id, ref['residRef'], provider))

    for rendition in item.get('renditions', {}).values():
        href = service_provider.prepare_href(rendition['href'])
        if rendition['rendition'] == 'baseImage':
            tasks.append(archive_media.s(task_id, guid, href))
        else:
            tasks.append(archive_rendition.s(task_id, guid, rendition['rendition'], href))

    update_status(*finish_subtask_from_progress(task_id))
    if tasks:
        chord((task for task in tasks), update_item.s(crt_task_id == task_id, task_id, guid)).delay()
    elif task_id == crt_task_id:
        update_status(*finish_task_for_progress(task_id))


def ingest_set_archived(guid):
    ingest_doc = app.data.find_one('ingest', guid=guid, req=None)
    if ingest_doc:
        app.data.update('ingest', ingest_doc.get('_id'), {'archived': utcnow()})


class ArchiveIngestModel(BaseModel):
    endpoint_name = 'archive_ingest'
    resource_methods = ['POST']
    item_methods = ['GET']
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
        data = app.data
        for doc in docs:
            ingest_doc = data.find_one('ingest', guid=doc.get('guid'), req=None)
            if not ingest_doc:
                msg = 'Fail to found ingest item with guid: %s' % doc.get('guid')
                raise superdesk.SuperdeskError(payload=msg)
            ingest_set_archived(doc.get('guid'))

            doc.setdefault('_id', doc.get('guid'))
            doc.setdefault('user', str(getattr(flask.g, 'user', {}).get('_id')))
            data.insert('archive', [doc])

            task = archive_item.delay(doc.get('guid'), ingest_doc.get('ingest_provider'), doc.get('user'))
            doc['task_id'] = task.id
            data.update('archive', doc.get('guid'), {"task_id": task.id})

        return [doc.get('guid') for doc in docs]

    def update(self, id, updates, trigger_events=None):
        pass

    def delete(self, lookup, trigger_events=None):
        pass

    def find_one(self, req=None, **lookup):
        try:
            task_id = lookup["task_id"]
            task = AsyncResult(task_id)

            if task.state == 'PROGRESS' and task.result:
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
