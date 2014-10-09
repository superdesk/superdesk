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


def send_user_mentioned_email(recipients, user_name, doc, url):
    print('sending mention email to:', recipients)
    send_email.delay(subject='You were mentioned in a comment by %s' % user_name,
                     sender=ADMINS[0],
                     recipients=recipients,
                     text_body=render_template("user_mention.txt", text=doc['text'], username=user_name, link=url),
                     html_body=render_template("user_mention.html", text=doc['text'], username=user_name, link=url))


def send_email_to_mentioned_users(doc, mentioned_users, origin):
    prefs_service = superdesk.get_resource_service('preferences')
    recipients = []
    for user in mentioned_users:
        send_email = prefs_service.email_notification_is_enabled(user)
        if send_email:
            user_doc = superdesk.get_resource_service('users').find_one(req=None, _id=user)
            recipients.append(user_doc['email'])
    if recipients:
        username = g.user.get('display_name') or g.user.get('username')
        url = '{}/#/authoring/{}?comments={}'.format(origin, doc['item'], doc['_id'])
        send_user_mentioned_email(recipients, username, doc, url)


def get_users(usernames):
    req = ParsedRequest()
    users = superdesk.get_resource_service('users').get(req=req, lookup={'username': {'$in': usernames}})
    users = {user.get('username'): user.get('_id') for user in users}
    return users


def notify_mentioned_users(docs, origin):
    for doc in docs:
        mentioned_users = doc.get('mentioned_users', {}).values()
        add_activity('', type='comment', item=str(doc.get('item')),
                     comment=doc.get('text'), comment_id=str(doc.get('_id')),
                     notify=mentioned_users)
        send_email_to_mentioned_users(doc, mentioned_users, origin)
