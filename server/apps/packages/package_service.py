# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from eve.versioning import resolve_document_version
from settings import DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES
import superdesk
from collections import Counter
from eve.utils import config, ParsedRequest
from eve.validation import ValidationError
from superdesk.errors import SuperdeskApiError
from superdesk import get_resource_service
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, EMBARGO
from superdesk.metadata.packages import LINKED_IN_PACKAGES, PACKAGE_TYPE, TAKES_PACKAGE, PACKAGE, LAST_TAKE, \
    REFS, RESIDREF, GROUPS, ID_REF, MAIN_GROUP, SEQUENCE, ROOT_GROUP, ROLE, ROOT_ROLE, MAIN_ROLE, GROUP_ID
from apps.archive.common import insert_into_versions
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.utc import utcnow

logger = logging.getLogger(__name__)
package_create_signal = superdesk.signals.signal('package.create')  # @UndefinedVariable


def create_root_group(docs):
    """Define groups in given docs if not present or empty.

    :param docs: list of docs
    """
    for doc in docs:
        if len(doc.get(GROUPS, [])):
            continue
        doc[GROUPS] = [
            {GROUP_ID: ROOT_GROUP, ROLE: ROOT_ROLE, REFS: [{ID_REF: MAIN_GROUP}]},
            {GROUP_ID: MAIN_GROUP, ROLE: MAIN_ROLE, REFS: []}
        ]


def get_item_ref(item):
    """Get reference for given item which can be used in group.refs.

    :param item: item dict
    """
    return {
        RESIDREF: item.get('_id'),
        'headline': item.get('headline'),
        'slugline': item.get('slugline'),
        'location': 'archive',
        'itemClass': 'icls:' + item.get('type', 'text'),
        'renditions': item.get('renditions', {})
    }


class PackageService():
    def on_create(self, docs):
        create_root_group(docs)
        self.check_root_group(docs)
        self.check_package_associations(docs)

        for doc in docs:
            if not doc.get('ingest_provider'):
                doc['source'] = DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES

        package_create_signal.send(self, docs=docs)

    def on_created(self, docs):
        for (doc, assoc) in [(doc, assoc) for doc in docs
                             for assoc in self._get_associations(doc)]:
            self.update_link(doc, assoc)

    def on_update(self, updates, original):
        self.check_root_group([updates])
        associations = self._get_associations(updates)
        self.check_for_duplicates(original, associations)
        for assoc in associations:
            self.extract_default_association_data(original, assoc)

    def on_updated(self, updates, original):
        to_add = {assoc.get(RESIDREF): assoc for assoc in self._get_associations(updates)
                  if assoc.get(RESIDREF) and updates.get(GROUPS)}
        to_remove = (assoc for assoc in self._get_associations(original)
                     if assoc.get(RESIDREF) not in to_add)
        for assoc in to_remove:
            self.update_link(original, assoc, delete=True)
        for assoc in to_add.keys():
            self.update_link(original, to_add[assoc])

    def on_deleted(self, doc):
        for assoc in self._get_associations(doc):
            self.update_link(doc, assoc, delete=True)

    def check_root_group(self, docs):
        for groups in [doc.get(GROUPS) for doc in docs if doc.get(GROUPS)]:
            self.check_all_groups_have_id_set(groups)
            root_groups = [group for group in groups if group.get(GROUP_ID) == ROOT_GROUP]

            if len(root_groups) == 0:
                message = 'Root group is missing.'
                logger.error(message)
                raise SuperdeskApiError.forbiddenError(message=message)

            if len(root_groups) > 1:
                message = 'Only one root group is allowed.'
                logger.error(message)
                raise SuperdeskApiError.forbiddenError(message=message)

            self.check_that_all_groups_are_referenced_in_root(root_groups[0], groups)

    def check_all_groups_have_id_set(self, groups):
        if any(group for group in groups if not group.get(GROUP_ID)):
            message = 'Group is missing id.'
            logger.error(message)
            raise SuperdeskApiError.forbiddenError(message=message)

    def check_that_all_groups_are_referenced_in_root(self, root, groups):
        rest = [group.get(GROUP_ID) for group in groups if group.get(GROUP_ID) != ROOT_GROUP]
        refs = [ref.get(ID_REF) for group in groups for ref in group.get(REFS, [])
                if ref.get(ID_REF)]

        rest_counter = Counter(rest)
        if any(id for id, value in rest_counter.items() if value > 1):
            message = '{id} group is added multiple times.'.format(id=id)
            logger.error(message)
            raise SuperdeskApiError.forbiddenError(message=message)

        if len(rest) != len(refs):
            message = 'The number of groups and of referenced groups in the root group do not match.'
            logger.error(message)
            raise SuperdeskApiError.forbiddenError(message=message)

        if len(set(rest).intersection(refs)) != len(refs):
            message = 'Not all groups are referenced in the root group.'
            logger.error(message)
            raise SuperdeskApiError.forbiddenError(message=message)

    def check_package_associations(self, docs):
        for (doc, group) in ((doc, group) for doc in docs for group in doc.get(GROUPS, [])):
            associations = group.get(REFS, [])
            self.check_for_duplicates(doc, associations)
            for assoc in associations:
                self.extract_default_association_data(group, assoc)

    def extract_default_association_data(self, package, assoc):
        if assoc.get(ID_REF):
            return

        item, item_id, endpoint = self.get_associated_item(assoc)
        self.check_for_circular_reference(package, item_id)
        assoc['guid'] = item.get('guid', item_id)
        assoc['type'] = item.get('type')

    def get_associated_item(self, assoc, throw_if_not_found=True):
        endpoint = assoc.get('location', 'archive')
        item_id = assoc[RESIDREF]

        if not item_id:
            raise SuperdeskApiError.badRequestError("Package contains empty ResidRef!")

        item = get_resource_service(endpoint).find_one(req=None, _id=item_id)

        if not item and throw_if_not_found:
            message = 'Invalid item reference: ' + assoc[RESIDREF]
            logger.error(message)
            raise SuperdeskApiError.notFoundError(message=message)
        return item, item_id, endpoint

    def update_link(self, package, assoc, delete=False):
        # skip root node
        if assoc.get(ID_REF):
            return
        package_id = package[config.ID_FIELD]
        package_type = package.get(PACKAGE_TYPE)

        item, item_id, endpoint = self.get_associated_item(assoc, not delete)
        if not item and delete:
            # just exit, no point on complaining
            return

        two_way_links = [d for d in item.get(LINKED_IN_PACKAGES, []) if not d['package'] == package_id]

        if not delete:
            data = {PACKAGE: package_id}
            if package_type:
                data.update({PACKAGE_TYPE: TAKES_PACKAGE})
            two_way_links.append(data)

        updates = {LINKED_IN_PACKAGES: two_way_links}
        get_resource_service(endpoint).system_update(item_id, updates, item)

    def check_for_duplicates(self, package, associations):
        counter = Counter()
        package_id = package[config.ID_FIELD]
        for itemRef in [assoc[RESIDREF] for assoc in associations if assoc.get(RESIDREF)]:
            if itemRef == package_id:
                message = 'Trying to self reference as an association.'
                logger.error(message)
                raise SuperdeskApiError.forbiddenError(message=message)
            counter[itemRef] += 1

        if any(itemRef for itemRef, value in counter.items() if value > 1):
            message = 'Content associated multiple times'
            logger.error(message)
            raise SuperdeskApiError.forbiddenError(message=message)

    def check_for_circular_reference(self, package, item_id):
        if any(d for d in package.get(LINKED_IN_PACKAGES, []) if d['package'] == item_id):
            message = 'Trying to create a circular reference to: ' + item_id
            logger.error(message)
            raise ValidationError(message)
        else:
            # keep checking in the hierarchy
            for d in (d for d in package.get(LINKED_IN_PACKAGES, []) if 'package' in d):
                linked_package = get_resource_service(ARCHIVE).find_one(req=None, _id=d['package'])
                if linked_package:
                    self.check_for_circular_reference(linked_package, item_id)

    def get_packages(self, doc_id):
        """
        Retrieves package(s) if an article identified by doc_id is referenced in a package.

        :param: doc_id identifier of the item in the package
        :return: articles of type composite
        """

        query = {'$and': [{ITEM_TYPE: CONTENT_TYPE.COMPOSITE}, {'groups.refs.guid': doc_id}]}

        request = ParsedRequest()
        request.max_results = 100

        return get_resource_service(ARCHIVE).get_from_mongo(req=request, lookup=query)

    def remove_ref_from_inmem_package(self, package, ref_id):
        """
        Removes the reference with ref_id from non-root groups. If there is nothing left
        in that group then the group and its reference in root group is also removed.
        If the removed item was the last item then returns
        :param package: Package
        :param ref_id: Id of the reference to be removed
        :return: True if there are still references in the package, False otherwise
        """
        groups_to_be_removed = set()
        non_root_groups = [group for group in package.get(GROUPS, []) if group.get(GROUP_ID) != ROOT_GROUP]
        for non_rg in non_root_groups:
            refs = [r for r in non_rg.get(REFS, []) if r.get(RESIDREF, '') != ref_id]
            if len(refs) == 0:
                groups_to_be_removed.add(non_rg.get(GROUP_ID))
            non_rg[REFS] = refs

        if len(groups_to_be_removed) > 0:
            root_group = [group for group in package.get(GROUPS, []) if group.get(GROUP_ID) == ROOT_GROUP][0]
            refs = [r for r in root_group.get(REFS, []) if r.get(ID_REF) not in groups_to_be_removed]
            root_group[REFS] = refs
            removed_groups = [group for group in package.get(GROUPS, [])
                              if group.get(GROUP_ID) not in groups_to_be_removed]
            package[GROUPS] = removed_groups

            # return if the package has any items left in it
            return len(refs) > 0

        # still has items in the package
        return True

    def replace_ref_in_package(self, package, old_ref_id, new_ref_id):
        """
        Locates the reference with the old_ref_id and replaces with the new_ref_id
        :param package: Package
        :param old_ref_id: Old reference id
        :param new_ref_id: New reference id
        """
        non_root_groups = (group for group in package.get(GROUPS, []) if group.get(GROUP_ID) != ROOT_GROUP)
        for g in (ref for group in non_root_groups for ref in group.get(REFS, [])):
            if g.get(RESIDREF, '') == old_ref_id:
                g[RESIDREF] = new_ref_id
                g['guid'] = new_ref_id

    def update_field_in_package(self, package, ref_id, field, field_value):
        """
        Locates the reference with the ref_id and replaces field value
        :param package: Package
        :param ref_id: reference id
        :param field: field to be replaced
        :param field_value: value to be used
        """
        non_root_groups = (group for group in package.get(GROUPS, []) if group.get(GROUP_ID) != ROOT_GROUP)
        for g in (ref for group in non_root_groups for ref in group.get(REFS, [])):
            if g.get(RESIDREF, '') == ref_id:
                g[field] = field_value

    def remove_refs_in_package(self, package, ref_id_to_remove, processed_packages=None):
        """
        Removes residRef referenced by ref_id_to_remove from the package associations and returns the package id.
        Before removing checks if the package has been processed. If processed the package is skipped.
        In case of takes package, sequence is decremented and last_take field is updated.
        If sequence is zero then the takes package is deleted.
        :return: package[config.ID_FIELD]
        """
        groups = package[GROUPS]

        if processed_packages is None:
            processed_packages = []

        sub_package_ids = [ref['guid'] for group in groups
                           for ref in group[REFS] if ref.get('type') == CONTENT_TYPE.COMPOSITE]
        for sub_package_id in sub_package_ids:
            if sub_package_id not in processed_packages:
                sub_package = self.find_one(req=None, _id=sub_package_id)
                return self.remove_refs_in_package(sub_package, ref_id_to_remove)

        new_groups = [{GROUP_ID: group[GROUP_ID], ROLE: group.get(ROLE),
                       REFS: [ref for ref in group[REFS] if ref.get('guid') != ref_id_to_remove]}
                      for group in groups]
        new_root_refs = [{ID_REF: group[GROUP_ID]} for group in new_groups if group[GROUP_ID] != ROOT_GROUP]

        for group in new_groups:
            if group[GROUP_ID] == ROOT_GROUP:
                group[REFS] = new_root_refs
                break

        updates = {config.LAST_UPDATED: utcnow(), GROUPS: new_groups}

        # if takes package then adjust the reference.
        # safe to do this as take can only be in one takes package.
        delete_package = False
        if package.get(PACKAGE_TYPE) == TAKES_PACKAGE:
            new_sequence = package[SEQUENCE] - 1
            if new_sequence == 0:
                # remove the takes package.
                get_resource_service(ARCHIVE).delete_action({config.ID_FIELD: package[config.ID_FIELD]})
                delete_package = True
            else:
                updates[SEQUENCE] = new_sequence
                last_take_group = next(reference for reference in
                                       next(new_group.get(REFS) for new_group in new_groups if
                                            new_group[GROUP_ID] == MAIN_GROUP)
                                       if reference.get(SEQUENCE) == new_sequence)

                if last_take_group:
                    updates[LAST_TAKE] = last_take_group.get(RESIDREF)

        if not delete_package:
            resolve_document_version(updates, ARCHIVE, 'PATCH', package)
            get_resource_service(ARCHIVE).patch(package[config.ID_FIELD], updates)
            insert_into_versions(id_=package[config.ID_FIELD])

        sub_package_ids.append(package[config.ID_FIELD])
        return sub_package_ids

    def _get_associations(self, doc):
        return [assoc for group in doc.get(GROUPS, [])
                for assoc in group.get(REFS, [])]

    def remove_spiked_refs_from_package(self, doc_id):
        packages = self.get_packages(doc_id)
        if packages.count() > 0:
            processed_packages = []
            for package in packages:
                if str(package[config.ID_FIELD]) not in processed_packages:
                    processed_packages.extend(
                        self.remove_refs_in_package(package, doc_id, processed_packages))

    def get_residrefs(self, package):
        """
        Returns all residref in the package.

        :param package:
        :return: list of residref
        """
        return [ref.get(RESIDREF) for group in package.get(GROUPS, [])
                for ref in group.get(REFS, []) if RESIDREF in ref]

    def check_if_any_item_in_package_has_embargo(self, package):
        """
        Recursively checks if any item in the package has embargo.
        :raises: SuperdeskApiError.badRequestError() if any item in the package has embargo.
        """

        item_refs_in_package = self.get_residrefs(package)

        for item_ref in item_refs_in_package:
            doc = get_resource_service(ARCHIVE).find_one(req=None, _id=item_ref)

            if doc.get(EMBARGO):
                raise SuperdeskApiError.badRequestError("Package can't have item which has emabrgo. "
                                                        "Slugline/Unique Name of the item having embargo: %s/%s" %
                                                        (doc.get('slugline'), doc.get('unique_name')))

            if doc[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
                self.check_if_any_item_in_package_has_embargo(doc)

    def get_item_refs(self, package):
        """
        Returns all item references in the package.

        :param package:
        :return: list of item references
        """

        return [ref for group in package.get(GROUPS, []) for ref in group.get(REFS, []) if RESIDREF in ref]
