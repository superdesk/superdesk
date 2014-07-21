from superdesk.base_model import BaseModel
from flask import current_app as app
import flask
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
        user = getattr(flask.g, 'user') if hasattr(flask.g, 'user') else {}
        if not user:
            if app.debug:
                user = user or {}
            else:
                raise superdesk.SuperdeskError(payload='Invalid user.')
        payload = 'Commenting on behalf of someone else is prohibited.'
        for doc in docs:
            check_item_valid(doc['item'])
            sent_user = doc.get('user', None)
            if sent_user and sent_user != user.get('_id'):
                raise superdesk.SuperdeskError(payload=payload)
            doc['user'] = str(user.get('_id'))

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
