import re

from eve.utils import ParsedRequest
from flask import current_app as app
import flask

import superdesk
from superdesk.base_model import BaseModel
from superdesk.notification import push_notification


comments_schema = {
    'text': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 500,
        'required': True,
    },
    'item': BaseModel.rel('archive', True, True, type='string'),
    'user': BaseModel.rel('users', True),
    'mentioned_users': {
        'type': 'list',
        'schema': {
            'type': 'objectid'
        }
    }
}


def check_item_valid(item_id):
    item = app.data.find_one('archive', req=None, _id=item_id)
    if not item:
        msg = 'Invalid content item ID provided: %s' % item_id
        raise superdesk.SuperdeskError(payload=msg)


def get_users_mentions(text):
    usernames = []
    pattern = re.compile("\[([a-zA-Z]\w+)\]")
    for match in re.finditer(pattern, text):
        for username in match.groups():
            if username not in usernames:
                usernames.append(username)
    return usernames


def get_user_ids(usernames):
    req = ParsedRequest()
    users = superdesk.apps['users'].get(req=req, lookup={'username': {'$in': usernames}})
    user_ids = [user.get('_id') for user in users]
    return user_ids


def get_usernames(user_ids):
    req = ParsedRequest()
    users = superdesk.apps['users'].get(req=req, lookup={'_id': {'$in': user_ids}})
    usernames = [user.get('username') for user in users]
    return usernames


class ItemCommentsModel(BaseModel):
    endpoint_name = 'item_comments'
    schema = comments_schema
    resource_methods = ['GET', 'POST', 'DELETE']
    datasource = {'default_sort': [('_created', -1)]}

    def on_create(self, docs):
        for doc in docs:
            sent_user = doc.get('user', None)
            user = flask.g.user
            if sent_user and sent_user != user.get('_id'):
                payload = 'Commenting on behalf of someone else is prohibited.'
                raise superdesk.SuperdeskError(payload=payload)
            doc['user'] = str(user.get('_id'))
            usernames = get_users_mentions(doc.get('text'))
            doc['mentioned_users'] = get_user_ids(usernames)

    def on_created(self, docs):
        push_notification('archive_comment', created=1)
        for doc in docs:
            user_ids = doc.get('mentioned_users')
            if not user_ids:
                continue
            usernames = get_usernames(user_ids)
            for username in usernames:
                push_notification('archive_comment_user_mention',
                                  item_id=doc.get('item'), comment_id=str(doc.get('_id')),
                                  user_id=doc.get('user'), mentioned_username=username)

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
