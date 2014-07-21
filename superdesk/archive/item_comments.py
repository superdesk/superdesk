from superdesk.base_model import BaseModel
from flask import current_app as app
import superdesk
from superdesk.notification import push_notification


comments_schema = {
    'text': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 500,
        'required': True,
    },
    'item': {
        'type': 'string',
        'required': True,
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
}


def check_item_valid(item_id):
    item = app.data.find_one('archive', req=None, _id=item_id)
    if not item:
        msg = 'Invalid content item ID provided: %s' % item_id
        raise superdesk.SuperdeskError(payload=msg)


class ItemCommentsModel(BaseModel):
    endpoint_name = 'item_comments'
    schema = comments_schema
    resource_methods = ['GET', 'POST', 'DELETE']
    datasource = {'default_sort': [('_created', -1)]}

    def on_create(self, docs):
        for doc in docs:
            check_item_valid(doc['item'])

    def on_created(self, docs):
        push_notification('archive_comment', created=1)

    def on_updated(self, updates, original):
        push_notification('archive_comment', updated=1)

    def on_deleted(self, doc):
        push_notification('archive_comment', deleted=1)


class ItemCommentsSubModel(BaseModel):
    endpoint_name = 'content_item_comments'
    url = 'archive/<path:item>/comments'
    schema = comments_schema
    datasource = {'source': 'item_comments'}
    resource_methods = ['GET']

    def get(self, req, lookup):
        check_item_valid(lookup.get('item'))
        return super().get(req, lookup)
