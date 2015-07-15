# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from datetime import datetime
from uuid import uuid4

from eve.utils import config
import flask
from flask import current_app as app
from eve.versioning import insert_versioning_documents

from superdesk.celery_app import update_key
from superdesk.utc import utcnow, get_expiry_date
from settings import SERVER_DOMAIN
from superdesk import get_resource_service
from apps.content import metadata_schema
from superdesk.workflow import set_default_state, is_workflow_state_transition_valid
import superdesk
from apps.archive.archive import SOURCE as ARCHIVE
from apps.content import PACKAGE_TYPE, TAKES_PACKAGE
from superdesk.errors import SuperdeskApiError, IdentifierGenerationError

GUID_TAG = 'tag'
GUID_FIELD = 'guid'
GUID_NEWSML = 'newsml'
FAMILY_ID = 'family_id'
INGEST_ID = 'ingest_id'
ASSOCIATIONS = 'refs'
ITEM_REF = 'residRef'
ID_REF = 'idRef'
MAIN_GROUP = 'main'
ROOT_GROUP = 'root'
SEQUENCE = 'sequence'
PUBLISH_STATES = ['published', 'killed', 'corrected', 'scheduled']
CUSTOM_HATEOAS = {'self': {'title': 'Archive', 'href': '/archive/{_id}'}}
ITEM_OPERATION = 'operation'
ITEM_CREATE = 'create'
ITEM_UPDATE = 'update'
ITEM_RESTORE = 'restore'
ITEM_DUPLICATE = 'duplicate'
ITEM_DESCHEDULE = 'deschedule'
item_operations = [ITEM_CREATE, ITEM_UPDATE, ITEM_RESTORE, ITEM_DUPLICATE, ITEM_DESCHEDULE]


def update_version(updates, original):
    """Increment version number if possible."""
    if config.VERSION in updates and original.get('version', 0) == 0:
        updates.setdefault('version', updates[config.VERSION])


def on_create_item(docs, repo_type=ARCHIVE):
    """Make sure item has basic fields populated."""
    for doc in docs:
        update_dates_for(doc)
        set_original_creator(doc)

        if not doc.get(GUID_FIELD):
            doc[GUID_FIELD] = generate_guid(type=GUID_NEWSML)

        if 'unique_id' not in doc:
            generate_unique_id_and_name(doc, repo_type)

        if 'family_id' not in doc:
            doc['family_id'] = doc[GUID_FIELD]

        set_default_state(doc, 'draft')
        doc.setdefault('_id', doc[GUID_FIELD])
        if not doc.get(ITEM_OPERATION):
            doc[ITEM_OPERATION] = ITEM_CREATE


def on_duplicate_item(doc):
    """Make sure duplicated item has basic fields populated."""

    doc[GUID_FIELD] = generate_guid(type=GUID_NEWSML)
    generate_unique_id_and_name(doc)
    doc.setdefault('_id', doc[GUID_FIELD])


def update_dates_for(doc):
    for item in ['firstcreated', 'versioncreated']:
        doc.setdefault(item, utcnow())


def generate_guid(**hints):
    """Generate a GUID based on given hints"""
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
        raise SuperdeskApiError.notFoundError('Invalid user.')
    return user


def get_auth():
    auth = flask.g.get('auth', {})
    return auth


def set_original_creator(doc):
    usr = get_user()
    user = str(usr.get('_id', ''))
    doc['original_creator'] = user
    doc['sign_off'] = usr.get('sign_off', usr.get('username', ''))[:3]


def set_sign_off(updates, original):
    usr = get_user()
    if not usr:
        return

    sign_off = usr.get('sign_off', usr['username'][:3])
    current_sign_off = original.get('sign_off', '')

    if current_sign_off.endswith(sign_off):
        return

    updated_sign_off = '{}/{}'.format(current_sign_off, sign_off)
    updates['sign_off'] = updated_sign_off[1:] if updated_sign_off.startswith('/') else updated_sign_off


item_url = 'regex("[\w,.:_-]+")'

extra_response_fields = [GUID_FIELD, 'headline', 'firstcreated', 'versioncreated', 'archived']

aggregations = {
    'type': {'terms': {'field': 'type'}},
    'desk': {'terms': {'field': 'task.desk'}},
    'stage': {'terms': {'field': 'task.stage'}},
    'category': {'terms': {'field': 'anpa_category.name'}},
    'source': {'terms': {'field': 'source'}},
    'state': {'terms': {'field': 'state'}},
    'urgency': {'terms': {'field': 'urgency'}},
    'day': {'date_range': {'field': 'firstcreated', 'format': 'dd-MM-yyy HH:mm:ss', 'ranges': [{'from': 'now-24H'}]}},
    'week': {'date_range': {'field': 'firstcreated', 'format': 'dd-MM-yyy HH:mm:ss', 'ranges': [{'from': 'now-1w'}]}},
    'month': {'date_range': {'field': 'firstcreated', 'format': 'dd-MM-yyy HH:mm:ss', 'ranges': [{'from': 'now-1M'}]}},
}


def generate_unique_id_and_name(item, repo_type=ARCHIVE):
    """
    Generates and appends unique_id and unique_name to item.
    :throws IdentifierGenerationError: if unable to generate unique_id
    """

    try:
        key_name = 'TEST_{}_SEQ'.format(repo_type.upper()) if superdesk.app.config.get('SUPERDESK_TESTING', False) \
            else '{}_SEQ'.format(repo_type.upper())

        unique_id = update_key(key_name, flag=True)

        if unique_id:
            item['unique_id'] = unique_id
            item['unique_name'] = "#" + str(unique_id)
        else:
            raise IdentifierGenerationError()
    except Exception as e:
        raise IdentifierGenerationError() from e


def insert_into_versions(id_=None, doc=None):
    """
    There are some scenarios where the requests are not handled by eve. In those scenarios superdesk should be able to
    manually manage versions. Below are some scenarios:

    1.  When user fetches a content from ingest collection the request is handled by fetch API which doesn't
        extend from ArchiveResource.
    2.  When user submits content to a desk the request is handled by /tasks API.
    3.  When user publishes a package the items of the package also needs to be published. The publishing of items
        in the package is not handled by eve.
    """

    if id_:
        doc_in_archive_collection = get_resource_service(ARCHIVE).find_one(req=None, _id=id_)
    else:
        doc_in_archive_collection = doc

    if not doc_in_archive_collection:
        raise SuperdeskApiError.badRequestError(message='Document not found in archive collection')

    remove_unwanted(doc_in_archive_collection)
    if app.config['VERSION'] in doc_in_archive_collection:
        insert_versioning_documents(ARCHIVE, doc_in_archive_collection)


def remove_unwanted(doc):
    """
    As the name suggests this function removes unwanted attributes from doc to make an entry in Mongo and Elastic.
    """

    # _type attribute comes when queried against Elastic and desk comes while fetching an item from ingest
    for attr in ['_type', 'desk', 'archived']:
        if attr in doc:
            del doc[attr]


def is_assigned_to_a_desk(doc):
    """
    Returns True if the 'doc' is being submitted to a desk. False otherwise.

    :param doc: doc must be from archive collection
    :return: True if the 'doc' is being submitted to a desk, else False.
    """

    return doc.get('task') and doc['task'].get('desk')


def get_item_expiry(app, stage):
    expiry_minutes = app.settings['CONTENT_EXPIRY_MINUTES']
    if stage:
        expiry_minutes = stage.get('content_expiry', expiry_minutes)

    return get_expiry_date(expiry_minutes)


def get_expiry(desk_id=None, stage_id=None, desk_or_stage_doc=None):
    """
    Calculates the expiry for a content from fetching the expiry duration from one of the below
        1. desk identified by desk_id
        2. stage identified by stage_id. This will ignore desk_id if specified
        3. desk doc or stage doc identified by doc_or_stage_doc. This will ignore desk_id and stage_id if specified

    :param desk_id: desk identifier
    :param stage_id: stage identifier
    :param desk_or_stage_doc: doc from either desks collection or stages collection
    :return: when the doc will expire
    """

    stage = None

    if desk_or_stage_doc is None and desk_id:
        desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)

        if not desk:
            raise SuperdeskApiError.notFoundError('Invalid desk identifier %s' % desk_id)

        if not stage_id:
            stage = get_resource_service('stages').find_one(req=None, _id=desk['incoming_stage'])

            if not stage:
                raise SuperdeskApiError.notFoundError('Invalid stage identifier %s' % stage_id)

    if desk_or_stage_doc is None and stage_id:
        stage = get_resource_service('stages').find_one(req=None, _id=stage_id)

        if not stage:
                raise SuperdeskApiError.notFoundError('Invalid stage identifier %s' % stage_id)

    return get_item_expiry(app=app, stage=desk_or_stage_doc or stage)


def set_item_expiry(update, original):
    task = update.get('task', original.get('task', {}))
    desk_id = task.get('desk', None)
    stage_id = task.get('stage', None)

    if update == {}:
        original['expiry'] = get_expiry(desk_id, stage_id)
    else:
        update['expiry'] = get_expiry(desk_id, stage_id)


def update_state(original, updates):
    """
    Updates the 'updates' with a valid state if the state transition valid. If the content is in user's workspace and
    original['state'] is not draft then updates['state'] is set to 'draft'. If the content is in a desk then the state
    is changed to 'in-progress'.
    """

    original_state = original.get(config.CONTENT_STATE)
    if original_state not in ['ingested', 'in_progress', 'scheduled']:
        if original.get(PACKAGE_TYPE) == TAKES_PACKAGE:
            # skip any state transition validation for takes packages
            # also don't change the stage of the package
            return
        if not is_workflow_state_transition_valid('save', original_state):
            raise superdesk.InvalidStateTransitionError()
        elif is_assigned_to_a_desk(original):
            updates[config.CONTENT_STATE] = 'in_progress'
        elif not is_assigned_to_a_desk(original):
            updates[config.CONTENT_STATE] = 'draft'


def is_update_allowed(archive_doc):
    """
    Checks if the archive_doc is valid to be updated. If invalid then the method raises ForbiddenError.
    For instance, a published item shouldn't be allowed to update.
    """

    state = archive_doc.get(config.CONTENT_STATE)
    if state in ['killed']:
        raise SuperdeskApiError.forbiddenError("Item isn't in a valid state to be updated.")


def handle_existing_data(doc, pub_status_value='usable', doc_type='archive'):
    """
    Handles existing data. For now the below are handled:
        1. Sets the value of pubstatus property in metadata of doc in either ingest or archive repo
        2. Sets the value of marked_for_not_publication
    """

    if doc:
        if 'pubstatus' in doc:
            doc['pubstatus'] = doc.get('pubstatus', pub_status_value).lower()

        if doc_type == 'archive' and 'marked_for_not_publication' not in doc:
            doc['marked_for_not_publication'] = False


def item_schema(extra=None):
    """Create schema for item.

    :param extra: extra fields to be added to schema
    """
    schema = {
        'old_version': {
            'type': 'number',
        },
        'last_version': {
            'type': 'number',
        },
        'task': {'type': 'dict'},
        'publish_schedule': {
            'type': 'datetime',
            'nullable': True
        },
        'marked_for_not_publication': {
            'type': 'boolean',
            'default': False
        },
        ITEM_OPERATION: {
            'type': 'string',
            'allowed': item_operations,
            'index': 'not_analyzed'
        },
        'targeted_for': {
            'type': 'list',
            'nullable': True,
            'schema': {
                'type': 'dict',
                'schema': {
                    'name': {'type': 'string'},
                    'allow': {'type': 'boolean'}
                }
            }
        }
    }
    schema.update(metadata_schema)
    if extra:
        schema.update(extra)
    return schema
