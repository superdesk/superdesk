from superdesk.base_model import BaseModel
from components.item_lock import ItemLock
from models.io.eve import Eve
from flask import request
from superdesk import SuperdeskError
import flask


class ArchiveLockModel(BaseModel):
    endpoint_name = 'archive_lock'
    url = 'archive/<regex("[a-zA-Z0-9:\\-\\.]+"):item_id>/lock'
    schema = {
        'lock_user': {'type': 'string'}
    }
    datasource = {'backend': 'custom'}
    resource_methods = ['GET', 'POST']

    def on_create(self, docs):
        user = getattr(flask.g, 'user', None)
        if not user:
            raise SuperdeskError('User must me authenticated to perform an archive lock.')
        c = ItemLock(Eve())
        docs.clear()
        docs.append(c.lock({'_id': request.view_args['item_id']}, user['_id'], None))
