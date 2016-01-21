# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.activity import add_activity
from eve.utils import ParsedRequest
from flask import g
from superdesk.emails import send_user_mentioned_email
import re
import superdesk
from superdesk.notification import push_notification


def get_mentions(text):
    """
    Returns the names of desks and users from a given text
    User names starts with '@' and desk names starts with '#'
    """
    user_pattern = re.compile("(^|\s)\@([a-zA-Z0-9-_.]\w+)")
    desk_pattern = re.compile("(^|\s)\#([a-zA-Z0-9-_.]\w+)")
    raw_user_names = set(username for match in re.finditer(user_pattern, text) for username in match.groups())
    raw_desk_names = set(deskname for match in re.finditer(desk_pattern, text) for deskname in match.groups())
    desk_names = [d.replace('_', ' ') for d in raw_desk_names if d.strip()]
    user_names = [u for u in raw_user_names if u.strip()]
    return user_names, desk_names


def send_email_to_mentioned_users(doc, mentioned_users, origin):
    prefs_service = superdesk.get_resource_service('preferences')
    recipients = []
    for user in mentioned_users:
        send_email = prefs_service.email_notification_is_enabled(user_id=user)
        if send_email:
            user_doc = superdesk.get_resource_service('users').find_one(req=None, _id=user)
            recipients.append(user_doc['email'])
    if recipients:
        username = g.user.get('display_name') or g.user.get('username')
        url = '{}/#/workspace?item={}&action=edit&comments={}'.format(origin, doc['item'], doc['_id'])
        send_user_mentioned_email(recipients, username, doc, url)


def get_users(user_names):
    req = ParsedRequest()
    users = superdesk.get_resource_service('users').get(req=req, lookup={'username': {'$in': user_names}})
    users = {user.get('username'): user.get('_id') for user in users}
    return users


def get_desks(desk_names):
    req = ParsedRequest()
    desks = superdesk.get_resource_service('desks').get(req=req, lookup={'name': {'$in': desk_names}})
    desks = {desk.get('name'): desk.get('_id') for desk in desks}
    return desks


def notify_mentioned_users(docs, origin):
    for doc in docs:
        mentioned_users = doc.get('mentioned_users', {}).values()
        if len(mentioned_users) > 0:
            item = superdesk.get_resource_service('archive').find_one(req=None, _id=doc['item'])
            add_activity('user:mention', '', resource=None, type='comment', item=item,
                         comment=doc.get('text'), comment_id=str(doc.get('_id')),
                         notify=mentioned_users)
            send_email_to_mentioned_users(doc, mentioned_users, origin)


def notify_mentioned_desks(docs):
    for doc in docs:
        mentioned_desks = doc.get('mentioned_desks', {}).values()
        if len(mentioned_desks) > 0:
            item = superdesk.get_resource_service('archive').find_one(req=None, _id=doc['item'])
            add_activity('desk:mention', '', resource=None, type='comment', item=item,
                         comment=doc.get('text'), comment_id=str(doc.get('_id')),
                         notify_desks=mentioned_desks)


def on_activity_updated(updates, original):
    if original.get('desk', '') != '':
        push_notification('desk:mention')
