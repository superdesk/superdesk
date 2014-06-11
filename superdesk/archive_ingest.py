'''
Created on May 23, 2014

@author: Ioan v. Pocol
'''

from celery.canvas import chord
import flask

import superdesk
from superdesk.io import providers

from .utc import utc, utcnow
from superdesk.celery_app import celery, app
from celery.result import AsyncResult


def update_progress(task_id, value):
    # TODO: finish it
    task = AsyncResult(task_id)
    state = task.state
    if not state:
        assert(value > 0)
        current = 0
        total = value
    else:
        # TODO: get crt total and current
        print(state)

    print('update: current=', current, ', total=', total)
    task.update_state(state='PROGRESS', meta={'current': current, 'total': total})


@celery.task()
def archive_media(task_id, guid, href):
    # TODO: download from href and save file on app storage,
    # process it and update original rendition for guid content item
    pass


@celery.task()
def archive_rendition(task_id, guid, name, href):
    # TODO: download from href and save on app storage and update the 'name' rendition for guid content item
    pass


@celery.task()
def update_item(result, task_id, guid):
    # update import status as done
    app.data.update('archive', guid, {"task_id": ""})


@celery.task()
def archive_item(guid, provider, user, task_id=None):
    data = app.data
    crt_task_id = archive_item.request.id
    if not task_id:
        task_id = crt_task_id

    service_provider = providers[provider]
    service_provider.provider = data.find_one('ingest_providers', type=provider)

    item = None
    try:
        items = service_provider.get_items(guid)
    except Exception:
        # TODO: if ingest not available save error on task result
        # if service is not available set a retry and update task status
        return

    for item_it in items:
        if item_it['guid'] == guid:
            item = item_it
            break

    if item is None:
        # TODO: save error on task result
        return

    item['created'] = item['firstcreated'] = utc.localize(item['firstcreated'])
    item['updated'] = item['versioncreated'] = utc.localize(item['versioncreated'])
    data.update('archive', guid, item)

    tasks = []

    for group in item.get('groups', []):
        for ref in group.get('refs', []):
            if 'residRef' in ref:
                doc = {'guid': ref.get('residRef'), 'provider': provider, 'user': user, 'task_id': crt_task_id}

                archived_doc = data.find_one('archive', guid=doc.get('guid'))
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

    for rendition in item.get('renditions', []).values():
        href = service_provider.prepare_href(rendition['href'])
        if rendition['rendition'] == 'baseImage':
            tasks.append(archive_media.s(task_id, guid, href))
        else:
            tasks.append(archive_rendition.s(task_id, guid, rendition['rendition'], href))

    if tasks:
        chord((task for task in tasks), update_item.s(task_id, guid)).delay()


def ingest_set_archived(guid):
    ingest_doc = app.data.find_one('ingest', guid=guid)
    if ingest_doc:
        app.data.update('ingest', ingest_doc.get('_id'), {'archived': utcnow()})


def archive_ingest(data, docs, **kwargs):
    data = app.data
    for doc in docs:
        doc.setdefault('_id', doc.get('guid'))
        doc.setdefault('user', str(getattr(flask.g, 'user', {}).get('_id')))
        data.insert('archive', [doc])
        task = archive_item.delay(doc.get('guid'), doc.get('provider'), doc.get('user'))
        update_progress(task.id, 1)
        data.update('archive', doc.get('guid'), {"task_id": task.id})
        ingest_set_archived(doc.get('guid'))
    return [doc.get('guid') for doc in docs]


def read_status_archive_ingest(data, req, **lookup):
    # TODO: implement
    return {"task_id": lookup["task_id"], "status": "fake ingest status", "current": 10, "total": 20}

superdesk.connect('impl_insert:archive_ingest', archive_ingest)
superdesk.connect('impl_find_one:archive_ingest', read_status_archive_ingest)

superdesk.domain('archive_ingest', {
    'url': 'archive_ingest',
    'resource_title': 'archive_ingest',
    'resource_methods': ['POST'],
    'item_methods': ['GET'],
    'schema': {
        'provider': {
            'type': 'string',
            'required': True,
        },
        'guid': {
            'type': 'string',
            'required': True,
        },
    },
    'datasource': {
        'backend': 'noop'
    }
})
