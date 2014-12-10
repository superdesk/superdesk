from flask import current_app as app
from eve.utils import document_etag

import superdesk
from superdesk.celery_app import celery


def sync(resource, id):
    sync_delayed.delay(resource, str(id))


@celery.task
def sync_delayed(resource, id):
    """Sync document by given resource and id.

    :param resource: resource name
    :param id: id of document to be synced
    """
    backend = superdesk.get_backend()
    search_backend = backend._lookup_backend(resource)

    doc = backend.find_one_in_base_backend(resource, req=None, _id=id)
    if doc:
        doc.setdefault(app.config['ETAG'], document_etag(doc))
        search_backend.insert(resource, [doc])
    else:
        search_backend.remove(resource, _id=id)
