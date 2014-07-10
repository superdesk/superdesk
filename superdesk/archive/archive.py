from superdesk.base_model import BaseModel
from .common import base_schema, extra_response_fields, item_url, facets
from .common import on_create_item, on_create_media_archive, on_update_media_archive, on_delete_media_archive
from flask import current_app as app
from werkzeug.exceptions import NotFound
from superdesk.utc import utcnow


class ArchiveVersionsModel(BaseModel):
    endpoint_name = 'archive_versions'
    schema = base_schema
    extra_response_fields = extra_response_fields
    item_url = item_url
    resource_methods = []

    def on_create(self, docs):
        for doc in docs:
            doc['versioncreated'] = utcnow()


class ArchiveModel(BaseModel):
    endpoint_name = 'archive'
    schema = {}
    schema.update(base_schema)
    extra_response_fields = extra_response_fields
    item_url = item_url
    datasource = {
        'search_backend': 'elastic',
        'facets': facets
    }
    resource_methods = ['GET', 'POST', 'DELETE']
    versioning = True

    def on_create(self, docs):
        on_create_item(docs)

    def on_created(self, docs):
        on_create_media_archive()

    def on_update(self, updates, original):
        updates['versioncreated'] = utcnow()

    def on_updated(self, updates, original):
        on_update_media_archive()

    def on_delete(self, doc):
        '''Delete associated binary files.'''
        if doc and doc.get('renditions'):
            for _name, ref in doc['renditions'].items():
                try:
                    app.media.delete(ref['media'])
                except (KeyError, NotFound):
                    pass

    def on_deleted(self, doc):
        on_delete_media_archive()
