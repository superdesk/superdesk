from superdesk.base_model import BaseModel
from components.item_lock import ItemLock
from models.io.eve import Eve
from flask import request
from superdesk.archive.common import get_user


class ArchiveLockModel(BaseModel):
    endpoint_name = 'archive_lock'
    url = 'archive/<regex("[a-zA-Z0-9:\\-\\.]+"):item_id>/lock'
    schema = {
        'lock_user': {'type': 'string'}
    }
    datasource = {'backend': 'custom'}
    resource_methods = ['GET', 'POST']

    def on_create(self, docs):
        user = get_user()
        c = ItemLock(Eve())
        docs.clear()
        docs.append(c.lock({'_id': request.view_args['item_id']}, user['_id'], None))
