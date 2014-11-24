from superdesk.celery_app import celery
from flask import current_app as app
from eve.utils import document_etag


def create(endpoint_name, docs, **kwargs):
    create_delayed.delay(endpoint_name, docs, **kwargs)


@celery.task
def create_delayed(endpoint_name, docs, **kwargs):
    """Insert documents into given collection.
    :param endpoint_name: api resource name
    :param docs: list of docs to be inserted
    """

    search_backend = app.data._search_backend(endpoint_name)
    if not search_backend:
        return

    for doc in docs:
        doc.setdefault(app.config['ETAG'], document_etag(doc))

    search_backend.insert(endpoint_name, docs, **kwargs)
