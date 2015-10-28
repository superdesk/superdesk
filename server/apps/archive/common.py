# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from bson import ObjectId

import flask
from eve.utils import config
from datetime import datetime
from flask import current_app as app
from eve.versioning import insert_versioning_documents
from pytz import timezone

import superdesk
from superdesk.users.services import get_sign_off
from superdesk.celery_app import update_key
from superdesk.utc import utcnow, get_expiry_date
from settings import ORGANIZATION_NAME_ABBREVIATION
from superdesk import get_resource_service
from superdesk.metadata.item import metadata_schema, ITEM_STATE, CONTENT_STATE, \
    LINKED_IN_PACKAGES, BYLINE, SIGN_OFF, EMBARGO, ITEM_TYPE, CONTENT_TYPE
from superdesk.workflow import set_default_state, is_workflow_state_transition_valid
from superdesk.metadata.item import GUID_NEWSML, GUID_FIELD, GUID_TAG, not_analyzed
from superdesk.metadata.packages import PACKAGE_TYPE, TAKES_PACKAGE, SEQUENCE
from superdesk.metadata.utils import generate_guid
from superdesk.errors import SuperdeskApiError, IdentifierGenerationError
from apps.auth import get_user


ARCHIVE = 'archive'
CUSTOM_HATEOAS = {'self': {'title': 'Archive', 'href': '/archive/{_id}'}}
ITEM_OPERATION = 'operation'
ITEM_CREATE = 'create'
ITEM_UPDATE = 'update'
ITEM_RESTORE = 'restore'
ITEM_DUPLICATE = 'duplicate'
ITEM_DESCHEDULE = 'deschedule'
item_operations = [ITEM_CREATE, ITEM_UPDATE, ITEM_RESTORE, ITEM_DUPLICATE, ITEM_DESCHEDULE]
# part the task dict
LAST_AUTHORING_DESK = 'last_authoring_desk'
LAST_PRODUCTION_DESK = 'last_production_desk'


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

        if 'event_id' not in doc:
            doc['event_id'] = generate_guid(type=GUID_TAG)

        set_default_state(doc, CONTENT_STATE.DRAFT)
        doc.setdefault(config.ID_FIELD, doc[GUID_FIELD])

        copy_metadata_from_user_preferences(doc, repo_type)

        if not doc.get(ITEM_OPERATION):
            doc[ITEM_OPERATION] = ITEM_CREATE


def format_dateline_to_locmmmddsrc(located, current_timestamp, source=ORGANIZATION_NAME_ABBREVIATION):
    """
    Formats dateline to "Location, Month Date Source -"

    :return: formatted dateline string
    """

    dateline_location = "{city_code}"
    dateline_location_format_fields = located.get('dateline', 'city')
    dateline_location_format_fields = dateline_location_format_fields.split(',')
    if 'country' in dateline_location_format_fields and 'state' in dateline_location_format_fields:
        dateline_location = "{city_code}, {state_code}, {country_code}"
    elif 'state' in dateline_location_format_fields:
        dateline_location = "{city_code}, {state_code}"
    elif 'country' in dateline_location_format_fields:
        dateline_location = "{city_code}, {country_code}"
    dateline_location = dateline_location.format(**located)

    if located['tz'] != 'UTC':
        current_timestamp = datetime.fromtimestamp(current_timestamp.timestamp(), tz=timezone(located['tz']))
    if current_timestamp.month == 9:
        formatted_date = 'Sept {}'.format(current_timestamp.strftime('%d'))
    elif 3 <= current_timestamp.month <= 7:
        formatted_date = current_timestamp.strftime('%B %d')
    else:
        formatted_date = current_timestamp.strftime('%b %d')

    return "{location} {mmmdd} {source} -".format(location=dateline_location.upper(), mmmdd=formatted_date,
                                                  source=source)


def on_duplicate_item(doc):
    """Make sure duplicated item has basic fields populated."""

    doc[GUID_FIELD] = generate_guid(type=GUID_NEWSML)
    generate_unique_id_and_name(doc)
    doc.setdefault('_id', doc[GUID_FIELD])
    set_sign_off(doc)


def update_dates_for(doc):
    for item in ['firstcreated', 'versioncreated']:
        doc.setdefault(item, utcnow())


def get_auth():
    auth = flask.g.get('auth', {})
    return auth


def set_original_creator(doc):
    usr = get_user()
    user = str(usr.get('_id', doc.get('original_creator', '')))
    doc['original_creator'] = user


def set_sign_off(updates, original=None, repo_type=ARCHIVE, user=None):
    """
    Set sign_off on updates object. Rules:
        1. updates['sign_off'] = original['sign_off'] + sign_off of the user performing operation.
        2. If the last modified user and the user performing operation are same then sign_off shouldn't change
    """

    if repo_type != ARCHIVE:
        return

    user = user if user else get_user()
    if not user:
        return

    sign_off = get_sign_off(user)
    current_sign_off = '' if original is None else original.get(SIGN_OFF, '')

    if current_sign_off.endswith(sign_off):
        return

    updated_sign_off = '{}/{}'.format(current_sign_off, sign_off)
    updates[SIGN_OFF] = updated_sign_off[1:] if updated_sign_off.startswith('/') else updated_sign_off


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


def remove_media_files(doc):
        """
        Removes the media files of the given doc if they are not references by any other
        story across all repos. Returns true if the medis files are removed.
        """
        print('Removing Media Files...')

        if doc.get(ITEM_TYPE) in [CONTENT_TYPE.PICTURE, CONTENT_TYPE.VIDEO, CONTENT_TYPE.AUDIO]:
            base_image_id = doc.get('renditions', {}).get('baseImage', {}).get('media')

            if base_image_id:
                try:
                    archive_docs = superdesk.get_resource_service('archive'). \
                        get_from_mongo(None, {'renditions.baseImage.media': base_image_id})
                    ingest_docs = superdesk.get_resource_service('ingest'). \
                        get_from_mongo(None, {'renditions.baseImage.media': base_image_id})
                    legal_archive_docs = superdesk.get_resource_service('legal_archive'). \
                        get_from_mongo(None, {'renditions.baseImage.media': base_image_id})
                    archive_version_docs = superdesk.get_resource_service('archive_versions'). \
                        get_from_mongo(None, {'renditions.baseImage.media': base_image_id})
                    legal_archive_version_docs = superdesk.get_resource_service('legal_archive_versions'). \
                        get_from_mongo(None, {'renditions.baseImage.media': base_image_id})

                    if archive_docs.count() == 0 and ingest_docs.count() == 0 and legal_archive_docs.count() == 0 and \
                            archive_version_docs.count() == 0 and legal_archive_version_docs.count() == 0:
                        # there's no reference so do remove the file
                        for name, rendition in doc.get('renditions').items():
                            if 'media' in rendition:
                                print('Deleting media:{}'.format(rendition.get('media')))
                                app.media.delete(rendition.get('media'))
                        # files are removed
                        return True
                except Exception as ex:
                    print('Removing Media Exception:{}'.format(ex))
                    return False
        return False


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

    original_state = original.get(ITEM_STATE)
    if original_state not in {CONTENT_STATE.INGESTED, CONTENT_STATE.PROGRESS, CONTENT_STATE.SCHEDULED}:
        if original.get(PACKAGE_TYPE) == TAKES_PACKAGE:
            # skip any state transition validation for takes packages
            # also don't change the stage of the package
            return
        if not is_workflow_state_transition_valid('save', original_state):
            raise superdesk.InvalidStateTransitionError()
        elif is_assigned_to_a_desk(original):
            updates[ITEM_STATE] = CONTENT_STATE.PROGRESS
        elif not is_assigned_to_a_desk(original):
            updates[ITEM_STATE] = CONTENT_STATE.DRAFT


def is_update_allowed(archive_doc):
    """
    Checks if the archive_doc is valid to be updated. If invalid then the method raises ForbiddenError.
    For instance, a published item shouldn't be allowed to update.
    """

    if archive_doc.get(ITEM_STATE) == CONTENT_STATE.KILLED:
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


def validate_schedule(schedule, package_sequence=1):
    """
    Validates the publish schedule.
    :param datetime schedule: schedule datetime
    :param int package_sequence: takes package sequence.
    :raises: SuperdeskApiError.badRequestError if following cases
        - Not a valid datetime
        - Less than current utc time
        - if more than 1 takes exist in the package.
    """
    if schedule:
        if not isinstance(schedule, datetime):
            raise SuperdeskApiError.badRequestError("Schedule date is not recognized")
        if schedule < utcnow():
            raise SuperdeskApiError.badRequestError("Schedule cannot be earlier than now")
        if package_sequence > 1:
            raise SuperdeskApiError.badRequestError("Takes cannot be scheduled.")


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
        },
        'event_id': {
            'type': 'string',
            'mapping': not_analyzed
        },
        'rewrite_of': {
            'type': 'string',
            'mapping': not_analyzed,
            'nullable': True
        },
        SEQUENCE: {
            'type': 'integer'
        },
        EMBARGO: {
            'type': 'datetime',
            'nullable': True
        }
    }
    schema.update(metadata_schema)
    if extra:
        schema.update(extra)
    return schema


def is_item_in_package(item):
    """
    Checks if the passed item is a member of a non-takes package
    :param item:
    :return: True if the item belongs to a non-takes package
    """
    return item.get(LINKED_IN_PACKAGES, None) \
        and sum(1 for x in item.get(LINKED_IN_PACKAGES, []) if x.get(PACKAGE_TYPE, '') == '')


def is_normal_package(doc):
    """
    Returns True if the passed doc is a package and not a takes package. Otherwise, returns False.

    :return: True if it's a Package and not a Takes Package, False otherwise.
    """

    return not is_takes_package(doc)


def is_takes_package(doc):
    """
    Returns True if the passed doc is a takes package. Otherwise, returns False.

    :return: True if it's a Takes Package, False otherwise.
    """

    return doc[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE and doc.get(PACKAGE_TYPE, '') == TAKES_PACKAGE


def convert_task_attributes_to_objectId(doc):
    """
    set the task attributes desk, stage, user as object id
    :param doc:

    """
    task = doc.get('task', {})

    if not task:
        return

    if ObjectId.is_valid(task.get('desk')) and not isinstance(task.get('desk'), ObjectId):
        task['desk'] = ObjectId(task.get('desk'))
    if ObjectId.is_valid(task.get('stage')) and not isinstance(task.get('stage'), ObjectId):
        task['stage'] = ObjectId(task.get('stage'))
    if ObjectId.is_valid(task.get('user')) and not isinstance(task.get('user'), ObjectId):
        task['user'] = ObjectId(task.get('user'))
    if ObjectId.is_valid(task.get(LAST_PRODUCTION_DESK)) and \
            not isinstance(task.get(LAST_PRODUCTION_DESK), ObjectId):
        task[LAST_PRODUCTION_DESK] = ObjectId(task.get(LAST_PRODUCTION_DESK))
    if ObjectId.is_valid(task.get(LAST_AUTHORING_DESK, None)) and \
            not isinstance(task.get(LAST_AUTHORING_DESK), ObjectId):
        task[LAST_AUTHORING_DESK] = ObjectId(task.get(LAST_AUTHORING_DESK))


def copy_metadata_from_user_preferences(doc, repo_type=ARCHIVE):
    """
    Copies following properties: byline, signoff, dateline.located, place from user preferences to doc if the repo_type
    is Archive.

    About Dateline: Dateline has 3 parts: Located, Date (Format: Month Day) and Source. Dateline can either be simple:
    Sydney, July 30 AAP - or can be complex: Surat,Gujarat,IN, July 30 AAP -. Date in the dateline is timezone
    sensitive to the Located.  Located is set on the article based on user preferences if available. If located is not
    available in user preferences then dateline in full will not be set.
    """

    if repo_type == ARCHIVE:
        user = get_user()

        if 'dateline' not in doc:
            current_date_time = dateline_ts = utcnow()
            doc['dateline'] = {'date': current_date_time, 'source': ORGANIZATION_NAME_ABBREVIATION, 'located': None,
                               'text': None}

            if user and user.get('user_preferences', {}).get('dateline:located'):
                located = user.get('user_preferences', {}).get('dateline:located', {}).get('located')
                if located:
                    doc['dateline']['located'] = located
                    doc['dateline']['text'] = format_dateline_to_locmmmddsrc(located, dateline_ts)

        if BYLINE not in doc and user and user.get(BYLINE):
                doc[BYLINE] = user[BYLINE]

        if 'place' not in doc and user:
            place_in_preference = user.get('user_preferences', {}).get('article:default:place')

            if place_in_preference:
                doc['place'] = place_in_preference.get('place')

        set_sign_off(doc, repo_type=repo_type, user=user)
