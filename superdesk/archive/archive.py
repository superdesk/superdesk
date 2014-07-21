from superdesk.base_model import BaseModel
from .common import base_schema, extra_response_fields, item_url, facets
from .common import on_create_item, on_create_media_archive, on_update_media_archive, on_delete_media_archive
from flask import current_app as app, request, Response
from werkzeug.exceptions import NotFound
from superdesk.utc import utcnow
from datetime import datetime
from settings import DATE_FORMAT
from eve.utils import config
from eve.versioning import resolve_document_version, insert_versioning_documents
from eve.methods.common import build_response_document
import superdesk
import json


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

    def on_replaced(self, document, original):
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


version_schema = {
    'old_version': {
        'type': 'string',
        'required': True
    },
    'last_version': {
        'type': 'string',
        'required': True
    }
}


bp = superdesk.Blueprint('archive_set_version', __name__)
superdesk.blueprint(bp)


@bp.route('/archive/<regex("[a-zA-Z0-9:\\-\\.]+"):item_id>/set-version', methods=['POST'])
def set_version(item_id):
    ver = json.loads(request.data.decode('utf_8'))
    old = app.data.find_one('archive_versions', req=None, _id_document=item_id, _version=int(ver['old_version']))
    if old is None:
        raise superdesk.SuperdeskError(payload='Invalid version %s' % ver['old_version'])
    curr = app.data.find_one('archive', req=None, _id=item_id)
    if curr is None:
        raise superdesk.SuperdeskError(payload='Invalid item id %s' % item_id)
    if curr['_version'] != int(ver['last_version']):
        raise superdesk.SuperdeskError(payload='Invalid last version %s' % ver['last_version'])
    old['_id'] = old['_id_document']
    old['_updated'] = old['versioncreated'] = utcnow()
    del old['_id_document']
    resolve_document_version(old, 'archive', 'PATCH', curr)
    superdesk.apps['archive'].replace(id=item_id, document=old, trigger_events=True)
    insert_versioning_documents('archive', old)
    old[config.STATUS] = config.STATUS_OK
    request.path = request.path[:request.path.find('/', request.path.find('/') + 1)]
    build_response_document(old, 'archive', [])
    for k, v in old.items():
        if isinstance(v, datetime):
            old[k] = v.strftime(DATE_FORMAT)
    return Response(status=201, response=json.dumps(old), content_type='text/json')
