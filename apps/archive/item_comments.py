import re

from eve.utils import ParsedRequest
from flask import current_app as app
import flask

import superdesk
from superdesk.resource import Resource
from superdesk.notification import push_notification
from apps.activity import add_activity
from superdesk.services import BaseService


comments_schema = {
    'text': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 500,
        'required': True,
    },
    'item': Resource.rel('archive', True, True, type='string'),
    'user': Resource.rel('users', True),
    'mentioned_users': {
        'type': 'dict'
    }
}


def check_item_valid(item_id):
    item = app.data.find_one('archive', req=None, _id=item_id)
    if not item:
        msg = 'Invalid content item ID provided: %s' % item_id
        raise superdesk.SuperdeskError(payload=msg)


def get_users_mentions(text):
    usernames = []
    pattern = re.compile("(^|\s)\@([a-zA-Z0-9-_.]\w+)")
    for match in re.finditer(pattern, text):
        for username in match.groups():
            if username not in usernames:
                usernames.append(username)
    return usernames


def get_users(usernames):
    req = ParsedRequest()
    users = superdesk.get_resource_service('users').get(req=req, lookup={'username': {'$in': usernames}})
    users = {user.get('username'): user.get('_id') for user in users}
    return users


class ItemCommentsResource(Resource):
    schema = comments_schema
    resource_methods = ['GET', 'POST', 'DELETE']
    datasource = {'default_sort': [('_created', -1)]}


class ItemCommentsService(BaseService):

    def on_create(self, docs):
        for doc in docs:
            sent_user = doc.get('user', None)
            user = flask.g.user
            if sent_user and sent_user != user.get('_id'):
                payload = 'Commenting on behalf of someone else is prohibited.'
                raise superdesk.SuperdeskError(payload=payload)
            doc['user'] = str(user.get('_id'))
            usernames = get_users_mentions(doc.get('text'))
            doc['mentioned_users'] = get_users(usernames)

    def on_created(self, docs):
        for doc in docs:
            push_notification('item:comment', item=str(doc.get('item')))
            mentioned_users = doc.get('mentioned_users', {}).values()
            add_activity('', type='comment', item=str(doc.get('item')),
                         comment=doc.get('text'), comment_id=str(doc.get('_id')),
                         notify=mentioned_users)

    def on_updated(self, updates, original):
        push_notification('item:comment', updated=1)

    def on_deleted(self, doc):
        push_notification('item:comment', deleted=1)


class ItemCommentsSubResource(Resource):
    url = 'archive/<path:item>/comments'
    schema = comments_schema
    datasource = {'source': 'item_comments'}
    resource_methods = ['GET']


class ItemCommentsSubService(BaseService):

    def get(self, req, lookup):
        check_item_valid(lookup.get('item'))
        return super().get(req, lookup)
