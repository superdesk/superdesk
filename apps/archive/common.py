from datetime import datetime
from uuid import uuid4

import flask

from superdesk.utc import utcnow
from settings import SERVER_DOMAIN
from superdesk import SuperdeskError
from superdesk.notification import push_notification
import superdesk


GUID_TAG = 'tag'
GUID_NEWSML = 'newsml'
ARCHIVE_MEDIA = 'archive_media'


class InvalidFileType(SuperdeskError):
    """Exception raised when receiving a file type that is not supported."""

    def __init__(self, type=None):
        super().__init__('Invalid file type %s' % type, payload={})


def on_create_item(docs):
    """Make sure item has basic fields populated."""
    for doc in docs:
        update_dates_for(doc)
        doc['original_creator'] = set_user(doc)

        if not doc.get('guid'):
            doc['guid'] = generate_guid(type=GUID_NEWSML)

        doc.setdefault('_id', doc['guid'])


def update_dates_for(doc):
    for item in ['firstcreated', 'versioncreated']:
        doc.setdefault(item, utcnow())


def generate_guid(**hints):
    '''Generate a GUID based on given hints'''
    newsml_guid_format = 'urn:newsml:%(domain)s:%(timestamp)s:%(identifier)s'
    tag_guid_format = 'tag:%(domain)s:%(year)d:%(identifier)s'

    if not hints.get('id'):
        hints['id'] = str(uuid4())

    t = datetime.today()

    if hints['type'].lower() == GUID_TAG:
        return tag_guid_format % {'domain': SERVER_DOMAIN, 'year': t.year, 'identifier': hints['id']}
    elif hints['type'].lower() == GUID_NEWSML:
        return newsml_guid_format % {'domain': SERVER_DOMAIN, 'timestamp': t.isoformat(), 'identifier': hints['id']}
    return None


def get_user(required=False):
    user = flask.g.get('user', {})
    if '_id' not in user and required:
        raise superdesk.SuperdeskError(payload='Invalid user.')
    return user


def get_auth():
    auth = flask.g.get('auth', {})
    return auth


def set_user(doc):
    usr = get_user()
    user = str(usr.get('_id', ''))
    sent_user = doc.get('user', None)
    if sent_user and user and sent_user != user:
        raise superdesk.SuperdeskError()
    doc['user'] = user
    return user


item_url = 'regex("[\w,.:_-]+")'

extra_response_fields = ['guid', 'headline', 'firstcreated', 'versioncreated', 'archived']

facets = {
    'type': {'terms': {'field': 'type'}},
    'provider': {'terms': {'field': 'provider'}},
    'urgency': {'terms': {'field': 'urgency'}},
    'subject': {'terms': {'field': 'subject.name'}},
    'place': {'terms': {'field': 'place.name'}},
    'versioncreated': {'date_histogram': {'field': 'versioncreated', 'interval': 'hour'}},
}


def on_create_media_archive():
    push_notification('media_archive', created=1)


def on_update_media_archive():
    push_notification('media_archive', updated=1)


def on_delete_media_archive():
    push_notification('media_archive', deleted=1)
