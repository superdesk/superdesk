from superdesk.base_model import BaseModel
from flask import current_app as app, request, Response
from superdesk.utc import utcnow
from datetime import datetime
from settings import DATE_FORMAT
from eve.utils import config
from eve.versioning import resolve_document_version, insert_versioning_documents
from eve.methods.common import build_response_document
import superdesk
import json


class ArchiveLockModel(BaseModel):
    endpoint_name = 'items_lock'
    url = 'archive/<regex("[a-zA-Z0-9:\\-\\.]+"):item_id>/lock'
    schema = {
        'item': {
            'type': 'string',
            'unique': True
        },
        'user': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'users',
                'field': '_id',
                'embeddable': True
            }
        },
        'lock_time': {
            'type': 'datetime'
        }
    }
    datasource = {'default_sort': [('lock_time', -1)]}
    resource_methods = ['GET', 'POST']
#     versioning = True

    def on_create(self, docs):
        print('create', docs)


bp = superdesk.Blueprint('archive_lock', __name__)
superdesk.blueprint(bp)


@bp.route('/barchive/<regex("[a-zA-Z0-9:\\-\\.]+"):item_id>/lock', methods=['POST'])
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
