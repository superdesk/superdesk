from superdesk.activity import add_activity
from eve.utils import ParsedRequest
from flask import g, render_template
from settings import ADMINS

from superdesk.emails import send_email

import re
import superdesk


def get_users_mentions(text):
    pattern = re.compile("(^|\s)\@([a-zA-Z0-9-_.]\w+)")
    usernames = set(username for match in re.finditer(pattern, text) for username in match.groups())
    return list(usernames)


def send_user_mentioned_email(recipients, user_name, doc):
    send_email.delay(subject='You were mentioned in a comment by %s' % user_name,
                     sender=ADMINS[0],
                     recipients=recipients,
                     text_body=render_template("user_mention.txt", data=doc, username=user_name),
                     html_body=render_template("user_mention.html", data=doc, username=user_name))


def send_email_to_mentioned_users(doc, mentioned_users):
    prefs_service = superdesk.get_resource_service('preferences')
    recipients = []
    for user in mentioned_users:
        send_email = prefs_service.get_user_preference(user, 'email:notification')
        if send_email and send_email.get('enabled', False):
            user_doc = superdesk.get_resource_service('users').find_one(req=None, _id=user)
            recipients.append(user_doc['email'])
    if recipients:
        username = g.user.get('display_name') or g.user.get('username')
        send_user_mentioned_email(recipients, username, doc)


def get_users(usernames):
    req = ParsedRequest()
    users = superdesk.get_resource_service('users').get(req=req, lookup={'username': {'$in': usernames}})
    users = {user.get('username'): user.get('_id') for user in users}
    return users


def notify_mentioned_users(docs):
    for doc in docs:
        mentioned_users = doc.get('mentioned_users', {}).values()
        add_activity('', type='comment', item=str(doc.get('item')),
                     comment=doc.get('text'), comment_id=str(doc.get('_id')),
                     notify=mentioned_users)
        send_email_to_mentioned_users(doc, mentioned_users)
