# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from copy import copy
from copy import deepcopy
from functools import partial
import logging
from superdesk import get_resource_service
from apps.content import push_content_notification
import superdesk
from superdesk.errors import InvalidStateTransitionError, SuperdeskApiError, PublishQueueError
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE, GUID_FIELD, ITEM_STATE, CONTENT_STATE, \
    PUBLISH_STATES, EMBARGO, PUB_STATUS
from superdesk.metadata.packages import SEQUENCE, LINKED_IN_PACKAGES, GROUPS, PACKAGE
from superdesk.metadata.utils import item_url
from superdesk.notification import push_notification
from superdesk.publish import SUBSCRIBER_TYPES
from superdesk.services import BaseService
from superdesk.utc import utcnow
from superdesk.workflow import is_workflow_state_transition_valid

from eve.utils import config
from eve.validation import ValidationError
from eve.versioning import resolve_document_version

from apps.archive.archive import ArchiveResource, SOURCE as ARCHIVE
from apps.archive.common import get_user, insert_into_versions, item_operations
from apps.archive.common import validate_schedule, ITEM_OPERATION, convert_task_attributes_to_objectId, is_genre, \
    BROADCAST_GENRE, get_expiry
from apps.common.components.utils import get_component
from apps.item_autosave.components.item_autosave import ItemAutosave
from apps.legal_archive.commands import import_into_legal_archive
from apps.packages import TakesPackageService
from apps.packages.package_service import PackageService
from apps.publish.published_item import LAST_PUBLISHED_VERSION, PUBLISHED
from settings import DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES


logger = logging.getLogger(__name__)

ITEM_PUBLISH = 'publish'
ITEM_CORRECT = 'correct'
ITEM_KILL = 'kill'
item_operations.extend([ITEM_PUBLISH, ITEM_CORRECT, ITEM_KILL])


class BasePublishResource(ArchiveResource):
    """
    Base resource class for "publish" endpoint.
    """

    def __init__(self, endpoint_name, app, service, publish_type):
        self.endpoint_name = 'archive_%s' % publish_type
        self.resource_title = endpoint_name

        self.datasource = {'source': ARCHIVE}

        self.url = 'archive/{}'.format(publish_type)
        self.item_url = item_url

        self.resource_methods = []
        self.item_methods = ['PATCH']

        self.privileges = {'PATCH': publish_type}
        super().__init__(endpoint_name, app=app, service=service)


class BasePublishService(BaseService):
    """
    Base service class for "publish" endpoint
    """

    publish_type = 'publish'
    published_state = 'published'

    non_digital = partial(filter, lambda s: s.get('subscriber_type', '') == SUBSCRIBER_TYPES.WIRE)
    digital = partial(filter, lambda s: (s.get('subscriber_type', '') in {SUBSCRIBER_TYPES.DIGITAL,
                                                                          SUBSCRIBER_TYPES.ALL}))
    takes_package_service = TakesPackageService()
    package_service = PackageService()

    def on_update(self, updates, original):
        self._validate(original, updates)
        self._set_updates(original, updates, updates.get(config.LAST_UPDATED, utcnow()))
        convert_task_attributes_to_objectId(updates)  # ???

    def on_updated(self, updates, original):
        original = get_resource_service(ARCHIVE).find_one(req=None, _id=original[config.ID_FIELD])
        updates.update(original)

        if updates[ITEM_OPERATION] != ITEM_KILL and \
                original.get(ITEM_TYPE) in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            get_resource_service('archive_broadcast').on_broadcast_master_updated(updates[ITEM_OPERATION], original)

        get_resource_service('archive_broadcast').reset_broadcast_status(updates, original)
        push_content_notification([updates])
        self._import_into_legal_archive(updates)

    def update(self, id, updates, original):
        """
        Handles workflow of each Publish, Corrected and Killed.
        """
        try:
            user = get_user()
            last_updated = updates.get(config.LAST_UPDATED, utcnow())
            auto_publish = updates.pop('auto_publish', False)

            if original[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                self._publish_package_items(original, updates)
                self._update_archive(original, updates, should_insert_into_versions=auto_publish)
            else:
                updated = deepcopy(original)
                updated.update(updates)
                # if target_for is set the we don't to digital client.
                targeted_for = updates.get('targeted_for', original.get('targeted_for'))
                if original[ITEM_TYPE] in {CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED} \
                        and not (targeted_for or is_genre(original, BROADCAST_GENRE)):

                    # check if item is in a digital package
                    package = self.takes_package_service.get_take_package(original)

                    if not package:
                        '''
                        If type of the item is text or preformatted then item need to be sent to
                        digital subscribers, so package the item as a take.
                        '''
                        package_id = self.takes_package_service.package_story_as_a_take(updated, {}, None)
                        package = get_resource_service(ARCHIVE).find_one(req=None, _id=package_id)

                    package_id = package[config.ID_FIELD]
                    package_updates = self.process_takes(updates_of_take_to_be_published=updates,
                                                         original_of_take_to_be_published=original,
                                                         package=package)

                    # If the original package is corrected then the next take shouldn't change it
                    # back to 'published'
                    preserve_state = package.get(ITEM_STATE, '') == CONTENT_STATE.CORRECTED and \
                        updates.get(ITEM_OPERATION, ITEM_PUBLISH) == ITEM_PUBLISH

                    self._set_updates(package, package_updates, last_updated, preserve_state)
                    package_updates.setdefault(ITEM_OPERATION, updates.get(ITEM_OPERATION, ITEM_PUBLISH))
                    self._update_archive(package, package_updates)
                    package.update(package_updates)
                    self._import_into_legal_archive(package)
                    self.update_published_collection(published_item_id=package_id)
                    """
                    This sequence is for test purposes, it will be removed once the feature is finished.
                    """
#                     package = get_resource_service('published').find_one(req=None, item_id=package_id)
#                     enqueue_item(package)

                self._update_archive(original, updated, should_insert_into_versions=auto_publish)
                self.update_published_collection(published_item_id=original[config.ID_FIELD], updated=updated)
                """
                This sequence is for test purposes, it will be removed once the feature is finished.
                """
#                 item = get_resource_service('published').find_one(req=None, item_id=original[config.ID_FIELD])
#                 enqueue_item(item)

            self._process_publish_updates(original, updates)
            push_notification('item:publish', item=str(id), unique_name=original['unique_name'],
                              desk=str(original.get('task', {}).get('desk', '')),
                              user=str(user.get(config.ID_FIELD, '')))
        except SuperdeskApiError as e:
            raise e
        except KeyError as e:
            raise SuperdeskApiError.badRequestError(
                message="Key is missing on article to be published: {}".format(str(e)))
        except Exception as e:
            logger.exception("Something bad happened while publishing %s".format(id))
            raise SuperdeskApiError.internalError(message="Failed to publish the item: {}".format(str(e)))

    def _validate(self, original, updates):
        self.raise_if_not_marked_for_publication(original)
        self.raise_if_invalid_state_transition(original)

        updated = original.copy()
        updated.update(updates)

        takes_package = self.takes_package_service.get_take_package(original)

        if self.publish_type == 'publish':
            # validate if take can be published
            if takes_package and not self.takes_package_service.can_publish_take(
                    takes_package, updates.get(SEQUENCE, original.get(SEQUENCE, 1))):
                raise PublishQueueError.previous_take_not_published_error(
                    Exception("Previous takes are not published."))

            validate_schedule(updated.get('publish_schedule'), takes_package.get(SEQUENCE, 1) if takes_package else 1)

            if original[ITEM_TYPE] != CONTENT_TYPE.COMPOSITE and updates.get(EMBARGO):
                get_resource_service(ARCHIVE).validate_embargo(updated)

        if self.publish_type in [ITEM_CORRECT, ITEM_KILL]:
            if updates.get(EMBARGO):
                raise SuperdeskApiError.badRequestError("Embargo can't be set after publishing")

            if updates.get('dateline'):
                raise SuperdeskApiError.badRequestError("Dateline can't be modified after publishing")

        validate_item = {'act': self.publish_type, 'type': original['type'], 'validate': updated}
        validation_errors = get_resource_service('validate').post([validate_item])
        if validation_errors[0]:
            raise ValidationError(validation_errors)

        if original[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
            package_validation_errors = []
            self._validate_package_contents(original, takes_package, package_validation_errors)
            if len(package_validation_errors) > 0:
                raise ValidationError(package_validation_errors)

            self._validate_package(original, updates)

    def _validate_package(self, package, updates):
        items = self.package_service.get_residrefs(package)
        if self.publish_type in [ITEM_CORRECT, ITEM_KILL]:
            removed_items, added_items = self._get_changed_items(items, updates)
            # we raise error if correction is done on a empty package. Kill is fine.
            if len(removed_items) == len(items) and len(added_items) == 0 and self.publish_type == ITEM_CORRECT:
                raise SuperdeskApiError.badRequestError("Corrected package cannot be empty!")

    def raise_if_not_marked_for_publication(self, original):
        if original.get('flags', {}).get('marked_for_not_publication', False):
            raise SuperdeskApiError.badRequestError('Cannot publish an item which is marked as Not for Publication')

    def raise_if_invalid_state_transition(self, original):
        if not is_workflow_state_transition_valid(self.publish_type, original[ITEM_STATE]):
            error_message = "Can't {} as item state is {}" if original[ITEM_TYPE] == CONTENT_TYPE.TEXT else \
                "Can't {} as either package state or one of the items state is {}"
            raise InvalidStateTransitionError(error_message.format(self.publish_type, original[ITEM_STATE]))

    def get_digital_id_for_package_item(self, package_item):
        """
        Finds the digital item id for a given item in a package
        :param package_item: item in a package
        :return string: Digital item id if there's one otherwise id of package_item
        """
        if package_item[ITEM_TYPE] not in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]:
            return package_item[config.ID_FIELD]
        else:
            package_item_takes_package_id = self.takes_package_service.get_take_package_id(package_item)
            if not package_item_takes_package_id:
                return package_item[config.ID_FIELD]
            return package_item_takes_package_id

    def _process_publish_updates(self, original, updates):
        """ Common updates for published items """
        desk = None
        if original.get('task', {}).get('desk'):
            desk = get_resource_service('desks').find_one(req=None, _id=original['task']['desk'])
        if not original.get('ingest_provider'):
            updates['source'] = desk['source'] if desk and desk.get('source', '') \
                else DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES
        updates['pubstatus'] = PUB_STATUS.CANCELED if self.publish_type == 'kill' else PUB_STATUS.USABLE
        self._set_item_expiry(updates, original)

    def _set_item_expiry(self, updates, original):
        """
        Set the expiry for the item
        :param dict updates: doc on which publishing action is performed
        """
        desk_id = original.get('task', {}).get('desk')
        stage_id = original.get('task', {}).get('stage')
        offset = updates.get(EMBARGO, original.get(EMBARGO)) or \
            updates.get('publish_schedule', original.get('publish_schedule'))
        updates['expiry'] = get_expiry(desk_id, stage_id, offset=offset)

    def _is_take_item(self, item):
        """ Returns True if the item was a take
        """
        return item[ITEM_TYPE] != CONTENT_TYPE.COMPOSITE and \
            (not (item.get('targeted_for') or is_genre(item, BROADCAST_GENRE)))

    def process_takes(self, updates_of_take_to_be_published, package, original_of_take_to_be_published=None):
        """
        Primary rule for publishing a Take in Takes Package is: all previous takes must be published before a take
        can be published.

        Also, generates body_html of the takes package and make sure the metadata for the package is the same as the
        metadata of the take to be published.

        :param dict updates_of_take_to_be_published: updates for the take to be published
        :param dict package: Takes package to publish
        :param dict original_of_take_to_be_published: original of the take to be published
        :return: Takes Package Updates
        """

        takes = self.takes_package_service.get_published_takes(package)
        body_html = updates_of_take_to_be_published.get('body_html',
                                                        original_of_take_to_be_published.get('body_html', ''))
        package_updates = {}

        groups = package.get(GROUPS, [])
        if groups:
            take_refs = [ref for group in groups if group['id'] == 'main' for ref in group.get('refs')]
            sequence_num_of_take_to_be_published = 0
            take_article_id = updates_of_take_to_be_published.get(
                config.ID_FIELD, original_of_take_to_be_published[config.ID_FIELD])

            for r in take_refs:
                if r[GUID_FIELD] == take_article_id:
                    sequence_num_of_take_to_be_published = r[SEQUENCE]
                    r['is_published'] = True
                    break

            if takes and self.published_state != 'killed':
                body_html_list = [take.get('body_html', '') for take in takes]
                if self.published_state == 'published':
                    body_html_list.append(body_html)
                else:
                    body_html_list[sequence_num_of_take_to_be_published - 1] = body_html

                package_updates['body_html'] = '<br>'.join(body_html_list)
            else:
                package_updates['body_html'] = body_html

            metadata_tobe_copied = self.takes_package_service.fields_for_creating_take.copy()
            metadata_tobe_copied.extend(['publish_schedule', 'byline'])
            updated_take = original_of_take_to_be_published.copy()
            updated_take.update(updates_of_take_to_be_published)
            metadata_from = updated_take
            # this rules has changed to use the last published metadata
            # per ticket SD-3885
            # if self.published_state == 'corrected' and len(takes) > 1:
            #     # get the last take metadata only if there are more than one takes
            #     metadata_from = takes[-1]

            for metadata in metadata_tobe_copied:
                if metadata in metadata_from:
                    package_updates[metadata] = metadata_from.get(metadata)

            package_updates[GROUPS] = groups
            self.package_service.update_field_in_package(package_updates,
                                                         original_of_take_to_be_published[config.ID_FIELD],
                                                         config.VERSION,
                                                         updates_of_take_to_be_published[config.VERSION])

        return package_updates

    def _publish_package_items(self, package, updates):
        """
        Publishes all items of a package recursively then publishes the package itself
        :param package: package to publish
        :param updates: payload
        """
        items = self.package_service.get_residrefs(package)

        if len(items) == 0 and self.publish_type == ITEM_PUBLISH:
            raise SuperdeskApiError.badRequestError("Empty package cannot be published!")

        removed_items = []
        if self.publish_type in [ITEM_CORRECT, ITEM_KILL]:
            removed_items, added_items = self._get_changed_items(items, updates)
            # we raise error if correction is done on a empty package. Kill is fine.
            if len(removed_items) == len(items) and len(added_items) == 0 and self.publish_type == ITEM_CORRECT:
                raise SuperdeskApiError.badRequestError("Corrected package cannot be empty!")
            items.extend(added_items)

        if items:
            archive_publish = get_resource_service('archive_publish')
            for guid in items:
                package_item = super().find_one(req=None, _id=guid)

                if not package_item:
                    raise SuperdeskApiError.badRequestError(
                        "Package item with id: {} does not exist.".format(guid))

                if package_item[ITEM_STATE] not in PUBLISH_STATES:  # if the item is not published then publish it
                    if package_item[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                        # if the item is a package do recursion to publish
                        sub_updates = {i: updates[i] for i in ['state', 'operation'] if i in updates}
                        sub_updates['groups'] = list(package_item['groups'])
                        self._publish_package_items(package_item, sub_updates)
                        self._update_archive(original=package_item, updates=sub_updates,
                                             should_insert_into_versions=False)
                    else:
                        # publish the item
                        archive_publish.patch(id=package_item.pop(config.ID_FIELD), updates=package_item)

                    insert_into_versions(id_=guid)

                elif guid in removed_items:
                    # remove the package information from the package item.
                    linked_in_packages = [linked for linked in package_item.get(LINKED_IN_PACKAGES)
                                          if linked.get(PACKAGE) != package.get(config.ID_FIELD)]
                    super().system_update(guid, {LINKED_IN_PACKAGES: linked_in_packages}, package_item)

                package_item = super().find_one(req=None, _id=guid)
                self.package_service.update_field_in_package(updates, package_item[config.ID_FIELD],
                                                             config.VERSION, package_item[config.VERSION])

        updated = deepcopy(package)
        updated.update(updates)
        self.update_published_collection(published_item_id=package[config.ID_FIELD], updated=updated)

    def update_published_collection(self, published_item_id, updated=None):
        """
        Updates the published collection with the published item.
        Set the last_published_version to false for previous versions of the published items.
        :param: str published_item_id: _id of the document.
        """
        published_item = super().find_one(req=None, _id=published_item_id)
        published_item = copy(published_item)
        if updated:
            published_item.update(updated)
        published_item['is_take_item'] = self._is_take_item(published_item)
        if not published_item.get('digital_item_id'):
            published_item['digital_item_id'] = self.get_digital_id_for_package_item(published_item)
        get_resource_service(PUBLISHED).update_published_items(published_item_id, LAST_PUBLISHED_VERSION, False)
        return get_resource_service(PUBLISHED).post([published_item])

    def set_state(self, original, updates):
        """
        Set the state of the document based on the action (publish, correction, kill)
        :param dict original: original document
        :param dict updates: updates related to document
        """
        updates['publish_schedule'] = None
        updates[ITEM_STATE] = self.published_state

    def _set_updates(self, original, updates, last_updated, preserve_state=False):
        """
        Sets config.VERSION, config.LAST_UPDATED, ITEM_STATE in updates document.
        If item is being published and embargo is available then append Editorial Note with 'Embargoed'.

        :param dict original: original document
        :param dict updates: updates related to the original document
        :param datetime last_updated: datetime of the updates.
        """
        if not preserve_state:
            self.set_state(original, updates)
        updates.setdefault(config.LAST_UPDATED, last_updated)

        if original[config.VERSION] == updates.get(config.VERSION, original[config.VERSION]):
            resolve_document_version(document=updates, resource=ARCHIVE, method='PATCH', latest_doc=original)
            resolve_document_version(document=updates, resource=ARCHIVE, method='PATCH', latest_doc=original)

        if updates.get(EMBARGO, original.get(EMBARGO)) \
                and updates.get('ednote', original.get('ednote', '')).find('Embargo') == -1:
            updates['ednote'] = '{} {}'.format(original.get('ednote', ''), 'Embargoed.').strip()

    def _update_archive(self, original, updates, versioned_doc=None, should_insert_into_versions=True):
        """
        Updates the articles into archive collection and inserts the latest into archive_versions.
        Also clears autosaved versions if any.
        :param: versioned_doc: doc which can be inserted into archive_versions
        :param: should_insert_into_versions if True inserts the latest document into versions collection
        """

        self.backend.update(self.datasource, original[config.ID_FIELD], updates, original)

        if should_insert_into_versions:
            if versioned_doc is None:
                insert_into_versions(id_=original[config.ID_FIELD])
            else:
                insert_into_versions(doc=versioned_doc)

        get_component(ItemAutosave).clear(original[config.ID_FIELD])

    def _get_changed_items(self, existing_items, updates):
        """
        Returns the added and removed items from existing_items
        :param existing_items: Existing list
        :param updates: Changes
        :return: list of removed items and list of added items
        """
        if 'groups' in updates:
            new_items = self.package_service.get_residrefs(updates)
            removed_items = list(set(existing_items) - set(new_items))
            added_items = list(set(new_items) - set(existing_items))
            return removed_items, added_items
        else:
            return [], []

    def _validate_package_contents(self, package, takes_package, validation_errors=[]):
        """
        If the item passed is a package this function will ensure that the unpublished content validates and none of
        the content is locked by other than the publishing session, also do not allow any killed or spiked content

        :param package:
        :param takes_package:
        :param validation_errors: validation errors are appended if there are any.
        """
        # Ensure it is the sort of thing we need to validate
        if package[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE and not takes_package and self.publish_type == ITEM_PUBLISH:
            items = self.package_service.get_residrefs(package)

            # make sure package is not scheduled or spiked
            if package[ITEM_STATE] in (CONTENT_STATE.SPIKED, CONTENT_STATE.SCHEDULED):
                validation_errors.append('Package cannot be {}'.format(package[ITEM_STATE]))

            if package.get(EMBARGO):
                validation_errors.append('Package cannot have Embargo')

            if items:
                for guid in items:
                    doc = super().find_one(req=None, _id=guid)

                    if package[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                        digital = self.takes_package_service.get_take_package(doc) or {}
                        self._validate_package_contents(doc, digital, validation_errors)

                    # make sure no items are killed or spiked or scheduled
                    if doc[ITEM_STATE] in (CONTENT_STATE.KILLED, CONTENT_STATE.SPIKED, CONTENT_STATE.SCHEDULED):
                        validation_errors.append('Package cannot contain {} item'.format(doc[ITEM_STATE]))

                    if doc.get(EMBARGO):
                        validation_errors.append('Package cannot have Items with Embargo')

                    # don't validate items that already have published
                    if doc[ITEM_STATE] not in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]:
                        validate_item = {'act': self.publish_type, 'type': doc[ITEM_TYPE], 'validate': doc}
                        errors = get_resource_service('validate').post([validate_item], headline=True)
                        if errors[0]:
                            validation_errors.extend(errors[0])

                    # check the locks on the items
                    if doc.get('lock_session', None) and package['lock_session'] != doc['lock_session']:
                        validation_errors.extend(['{}: packaged item cannot be locked'.format(doc['headline'])])

    def _import_into_legal_archive(self, doc):
        """
        Import into legal archive async
        :param {dict} doc: document to be imported
        """

        if doc.get(ITEM_STATE) != CONTENT_STATE.SCHEDULED:
            kwargs = {
                'doc': doc
            }
            import_into_legal_archive.apply_async(kwargs=kwargs)  # @UndefinedVariable


superdesk.workflow_state('published')
superdesk.workflow_action(
    name='publish',
    include_states=['fetched', 'routed', 'submitted', 'in_progress', 'scheduled'],
    privileges=['publish']
)

superdesk.workflow_state('scheduled')
superdesk.workflow_action(
    name='schedule',
    include_states=['fetched', 'routed', 'submitted', 'in_progress'],
    privileges=['schedule']
)

superdesk.workflow_action(
    name='deschedule',
    include_states=['scheduled'],
    privileges=['deschedule']
)

superdesk.workflow_state('killed')
superdesk.workflow_action(
    name='kill',
    include_states=['published', 'scheduled', 'corrected'],
    privileges=['kill']
)

superdesk.workflow_state('corrected')
superdesk.workflow_action(
    name='correct',
    include_states=['published', 'corrected'],
    privileges=['correct']
)

superdesk.workflow_action(
    name='rewrite',
    include_states=['published', 'corrected'],
    privileges=['rewrite']
)
