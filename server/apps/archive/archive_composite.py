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
import superdesk

from collections import Counter
from eve.utils import config
from eve.validation import ValidationError
from superdesk.errors import SuperdeskApiError
from superdesk import get_resource_service
from apps.archive.archive import SOURCE as ARCHIVE
from apps.content import LINKED_IN_PACKAGES, PACKAGE_TYPE, TAKES_PACKAGE, ITEM_TYPE, ITEM_TYPE_COMPOSITE, PACKAGE
import pprint

ASSOCIATIONS = 'refs'
ITEM_REF = 'residRef'
ID_REF = 'idRef'
MAIN_GROUP = 'main'
ROOT_GROUP = 'root'
SEQUENCE = 'sequence'


logger = logging.getLogger(__name__)
package_create_signal = superdesk.signals.signal('package.create')


def create_root_group(docs):
    """Define groups in given docs if not present or empty.

    :param docs: list of docs
    """
    for doc in docs:
        if len(doc.get('groups', [])):
            continue
        doc['groups'] = [
            {'id': ROOT_GROUP, ASSOCIATIONS: [{ID_REF: MAIN_GROUP}]},
            {'id': MAIN_GROUP, ASSOCIATIONS: []}
        ]


def get_item_ref(item):
    """Get reference for given item which can be used in group.refs.

    :param item: item dict
    """
    return {
        ITEM_REF: item.get('_id'),
        'headline': item.get('headline'),
        'slugline': item.get('slugline'),
        'location': 'archive',
        'itemClass': 'icls:' + item.get('type', 'text'),
        'renditions': item.get('renditions', {}),
    }


class PackageService():

    def get_take_package_id(self, item):
        """
        Checks if the item is in a 'takes' package and returns the package id
        :return: _id of the package or None
        """
        takes_package = [package.get(PACKAGE) for package in item.get(LINKED_IN_PACKAGES, [])
                         if package.get(PACKAGE_TYPE)]
        if len(takes_package) > 1:
            message = 'Multiple takes found for item: {0}'.format(item['_id'])
            logger.error(message)
            raise SuperdeskApiError.forbiddenError(message=message)
        return takes_package[0] if takes_package else None

    def __link_items__(self, takes_package, target, link):
        sequence = takes_package.get(SEQUENCE, 0) if takes_package else 0
        main_group = next((group for group in takes_package['groups'] if group['id'] == MAIN_GROUP))

        if sequence == 0:
            target_ref = get_item_ref(target)
            sequence = self.__next_sequence__(sequence)
            target_ref[SEQUENCE] = sequence
            main_group[ASSOCIATIONS].append(target_ref)

        link_ref = get_item_ref(link)
        link_ref[SEQUENCE] = self.__next_sequence__(sequence)
        main_group[ASSOCIATIONS].append(link_ref)
        takes_package[SEQUENCE] = link_ref[SEQUENCE]

    def __next_sequence__(self, seq):
        return seq + 1

    def __copy_metadata__(self, target, to):
        to['headline'] = target.get('headline')  # + 1
        to['slugline'] = target.get('slugline')
        to['anpa_take_key'] = target.get('anpa_take_key')  # + 1

    def create_takes_package(self, target, link):
        # check if target has an associated takes package
        # if not, create it and add target as a take
        # check if the target is the last take, if not, resolve the last take
        # copy metadata from the target and add it as the next take
        # return the link item
        pp = pprint.PrettyPrinter(indent=4)
        takes_package_id = self.get_take_package_id(target)
        service = get_resource_service(ARCHIVE)

        if not link.get('_id'):
            # TODO: copy metadata from target, define what fields need to be copied
            self.__copy_metadata__(target, link)
            service.post([link])
            print('Saved link')
            pp.pprint(link)

        if not takes_package_id:
            takes_package = {
                ITEM_TYPE: ITEM_TYPE_COMPOSITE,
                PACKAGE_TYPE: TAKES_PACKAGE
            }
            create_root_group([takes_package])
            self.__link_items__(takes_package, target, link)
            print('Before saving')
            pp.pprint(takes_package)
            service.post([takes_package])
        else:
            takes_package = service.find_one(req=None, _id=takes_package_id)
            self.__link_items__(takes_package, target, link)
            print('Before updating package')
            pp.pprint(takes_package)
            del takes_package['_id']
            service.patch(takes_package_id, takes_package)

        print('Saved package')
        pp.pprint(takes_package)
        return link

    def on_create(self, docs):
        create_root_group(docs)
        self.check_root_group(docs)
        self.check_package_associations(docs)
        package_create_signal.send(self, docs=docs)

    def on_created(self, docs):
        for (doc, assoc) in [(doc, assoc) for doc in docs
                             for assoc in self._get_associations(doc)]:
            self.update_link(doc[config.ID_FIELD], assoc)

    def on_update(self, updates, original):
        self.check_root_group([updates])
        associations = self._get_associations(updates)
        self.check_for_duplicates(original, associations)
        for assoc in associations:
            self.extract_default_association_data(original, assoc)

    def on_updated(self, updates, original):
        toAdd = {assoc.get(ITEM_REF): assoc for assoc in self._get_associations(updates)}
        toRemove = [assoc for assoc in self._get_associations(original) if assoc.get(ITEM_REF) not in toAdd]
        for assoc in toRemove:
            self.update_link(original[config.ID_FIELD], assoc, delete=True)
        for assoc in toAdd.values():
            self.update_link(original[config.ID_FIELD], assoc)

    def on_deleted(self, doc):
        for assoc in self._get_associations(doc):
            self.update_link(doc[config.ID_FIELD], assoc, delete=True)

    def check_root_group(self, docs):
        for groups in [doc.get('groups') for doc in docs if doc.get('groups')]:
            self.check_all_groups_have_id_set(groups)
            root_groups = [group for group in groups if group.get('id') == 'root']

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
        if any(group for group in groups if not group.get('id')):
            message = 'Group is missing id.'
            logger.error(message)
            raise SuperdeskApiError.forbiddenError(message=message)

    def check_that_all_groups_are_referenced_in_root(self, root, groups):
        rest = [group.get('id') for group in groups if group.get('id') != 'root']
        refs = [ref.get('idRef') for group in groups for ref in group.get('refs', [])
                if ref.get('idRef')]

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
        for (doc, group) in [(doc, group) for doc in docs for group in doc.get('groups', [])]:
            associations = group.get(ASSOCIATIONS, [])
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
        item_id = assoc[ITEM_REF]
        item = get_resource_service(endpoint).find_one(req=None, _id=item_id)
        if not item and throw_if_not_found:
            message = 'Invalid item reference: ' + assoc[ITEM_REF]
            logger.error(message)
            raise SuperdeskApiError.notFoundError(message=message)
        return item, item_id, endpoint

    def update_link(self, package_id, assoc, delete=False):
        # skip root node
        if assoc.get(ID_REF):
            return

        item, item_id, endpoint = self.get_associated_item(assoc, not delete)
        if not item and delete:
            # just exit, no point on complaining
            return

        two_way_links = [d for d in item.get(LINKED_IN_PACKAGES, []) if not d['package'] == package_id]

        if not delete:
            two_way_links.append({PACKAGE: package_id, PACKAGE_TYPE: TAKES_PACKAGE})

        updates = self.get_item_update_data(item, two_way_links, delete)
        get_resource_service(endpoint).system_update(item_id, updates, item)

    """
    Add extensibility point for item patch data.
    """
    def get_item_update_data(self, __item, links, delete):
        return {LINKED_IN_PACKAGES: links}

    def check_for_duplicates(self, package, associations):
        counter = Counter()
        package_id = package[config.ID_FIELD]
        for itemRef in [assoc[ITEM_REF] for assoc in associations if assoc.get(ITEM_REF)]:
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

    def _get_associations(self, doc):
        return [assoc for group in doc.get('groups', [])
                for assoc in group.get(ASSOCIATIONS, [])]
