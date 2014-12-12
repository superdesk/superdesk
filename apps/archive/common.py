from datetime import datetime
from uuid import uuid4

import flask
from flask import current_app as app
from eve.versioning import insert_versioning_documents

from superdesk.celery_app import update_key
from superdesk.utc import utcnow
from settings import SERVER_DOMAIN
from superdesk import SuperdeskError, get_resource_service
from superdesk.notification import push_notification
from superdesk.workflow import set_default_state
import superdesk
from apps.archive.archive import SOURCE as ARCHIVE

GUID_TAG = 'tag'
GUID_NEWSML = 'newsml'
ARCHIVE_MEDIA = 'archive_media'


class InvalidFileType(SuperdeskError):
    """Exception raised when receiving a file type that is not supported."""

    def __init__(self, type=None):
        super().__init__('Invalid file type %s' % type, payload={})


class IdentifierGenerationError(SuperdeskError):
    """Exception raised if failed to generate unique_id."""

    status_code = 500
    payload = {'unique_id': 1}
    message = "Failed to generate unique_id"


def on_create_item(docs):
    """Make sure item has basic fields populated."""
    for doc in docs:
        update_dates_for(doc)
        set_original_creator(doc)

        if not doc.get('guid'):
            doc['guid'] = generate_guid(type=GUID_NEWSML)

        if 'unique_id' not in doc:
            generate_unique_id_and_name(doc)

        set_default_state(doc, 'draft')
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


def set_original_creator(doc):
    usr = get_user()
    user = str(usr.get('_id', ''))
    doc['original_creator'] = user

    # sent_user = doc.get('user', None)
    # if sent_user and user and sent_user != user:
    #     raise superdesk.SuperdeskError()
    # doc['user'] = user


item_url = 'regex("[\w,.:_-]+")'

extra_response_fields = ['guid', 'headline', 'firstcreated', 'versioncreated', 'archived']

aggregations = {
    'type': {'terms': {'field': 'type'}},
    'desk': {'terms': {'field': 'task.desk'}},
    'stage': {'terms': {'field': 'task.stage'}},
    'category': {'terms': {'field': 'anpa-category.name'}},
    'source': {'terms': {'field': 'source'}},
    'state': {'terms': {'field': 'state'}},
    'urgency': {'terms': {'field': 'urgency'}},
    'day': {'date_range': {'field': 'firstcreated', 'format': 'dd-MM-yyy HH:mm:ss', 'ranges': [{'from': 'now-24H'}]}},
    'week': {'date_range': {'field': 'firstcreated', 'format': 'dd-MM-yyy HH:mm:ss', 'ranges': [{'from': 'now-1w'}]}},
    'month': {'date_range': {'field': 'firstcreated', 'format': 'dd-MM-yyy HH:mm:ss', 'ranges': [{'from': 'now-1M'}]}},
}


def on_create_media_archive():
    push_notification('media_archive', created=1)


def on_update_media_archive():
    push_notification('media_archive', updated=1)


def on_delete_media_archive():
    push_notification('media_archive', deleted=1)


def generate_unique_id_and_name(item):
    """
    Generates and appends unique_id and unique_name to item.
    :throws IdentifierGenerationError: if unable to generate unique_id
    """

    try:
        unique_id = update_key("INGEST_SEQ", flag=True)

        if unique_id:
            item['unique_id'] = unique_id
            item['unique_name'] = "#" + str(unique_id)
        else:
            raise IdentifierGenerationError()
    except Exception as e:
        raise IdentifierGenerationError() from e


def insert_into_versions(guid, task_id=None):
    """
    There are some scenarios where the requests are not handled by eve. In those scenarios superdesk should be able to
    manually manage versions. Below are some scenarios:

    1.  When user fetches a content from ingest collection the request is delegated to a Celery Task. This gets complex
        when content is of type composite/package, in this case Celery task creates sub-tasks for each item in the
        package.
    2.  When user submits content to a desk the request is handled by /tasks API.
    """

    doc_in_archive_collection = get_resource_service(ARCHIVE).find_one(req=None, _id=guid)
    remove_unwanted(doc_in_archive_collection)

    if task_id is not None and 'task_id' not in doc_in_archive_collection:
        updates = get_resource_service(ARCHIVE).patch(guid, {"task_id": task_id, 'req_for_save': 'false'})
        doc_in_archive_collection.update(updates)

    if app.config['VERSION'] in doc_in_archive_collection:
        insert_versioning_documents(ARCHIVE, doc_in_archive_collection)


def remove_unwanted(doc):
    """
    As the name suggests this function removes unwanted attributes from doc to make an entry in Mongo and Elastic.
    """

    if '_type' in doc:
        del doc['_type']
