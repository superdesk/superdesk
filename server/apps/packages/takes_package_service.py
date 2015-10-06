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
import json
from eve.utils import config, ParsedRequest
from eve.versioning import resolve_document_version
from superdesk.errors import SuperdeskApiError, InvalidStateTransitionError
from superdesk import get_resource_service
from apps.archive.archive import SOURCE as ARCHIVE
from superdesk.metadata.packages import LINKED_IN_PACKAGES, PACKAGE_TYPE, TAKES_PACKAGE, PACKAGE, \
    LAST_TAKE, REFS, MAIN_GROUP, SEQUENCE, RESIDREF
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE, PUBLISH_STATES, ITEM_STATE, CONTENT_STATE, EMBARGO
from apps.archive.common import insert_into_versions
from .package_service import get_item_ref, create_root_group

logger = logging.getLogger(__name__)


class TakesPackageService():
    # metadata field of take
    fields_for_creating_take = ['headline', 'anpa_category', 'pubstatus',
                                'slugline', 'urgency', 'subject', 'dateline',
                                'place', 'priority', 'abstract', 'ednote', 'source']

    def get_take_package_id(self, item):
        """
        Checks if the item is in a 'takes' package and returns the package id
        :return: _id of the package or None
        """
        takes_package = [package.get(PACKAGE) for package in item.get(LINKED_IN_PACKAGES, [])
                         if package.get(PACKAGE_TYPE)]
        if len(takes_package) > 1:
            message = 'Multiple takes found for item: {0}'.format(item[config.ID_FIELD])
            logger.error(message)
            raise SuperdeskApiError.forbiddenError(message=message)
        return takes_package[0] if takes_package else None

    def get_take_package(self, item):
        package_id = self.get_take_package_id(item)
        takes_package = None

        if package_id:
            takes_package = get_resource_service(ARCHIVE).find_one(req=None, _id=package_id)

        return takes_package

    def enhance_with_package_info(self, item):
        package = self.get_take_package(item)
        if package:
            item.setdefault(TAKES_PACKAGE, package)

    def __link_items__(self, takes_package, target, link):
        sequence = takes_package.get(SEQUENCE, 0) if takes_package else 0
        main_group = next((group for group in takes_package['groups'] if group['id'] == MAIN_GROUP))

        if sequence == 0:
            target_ref = get_item_ref(target)
            sequence = self.__next_sequence__(sequence)
            target_ref[SEQUENCE] = sequence
            takes_package[SEQUENCE] = target_ref[SEQUENCE]
            takes_package[LAST_TAKE] = target[config.ID_FIELD]
            main_group[REFS].append(target_ref)

        if link is not None:
            link_ref = get_item_ref(link)
            link_ref[SEQUENCE] = self.__next_sequence__(sequence)
            main_group[REFS].append(link_ref)
            takes_package[SEQUENCE] = link_ref[SEQUENCE]
            takes_package[LAST_TAKE] = link[config.ID_FIELD]
            link[SEQUENCE] = link_ref[SEQUENCE]

    def __next_sequence__(self, seq):
        return seq + 1

    def __strip_take_info__(self, take_info):
        take_index = take_info.rfind('=')
        return take_info[0:take_index] if take_info[take_index + 1:].isdigit() else take_info

    def __copy_metadata__(self, target, to, package):
        # if target is the first take hence default sequence is for first take.
        sequence = package.get(SEQUENCE, 1) if package else 1
        sequence = self.__next_sequence__(sequence)
        take_key = self.__strip_take_info__(target.get('anpa_take_key', ''))
        to['event_id'] = target.get('event_id')
        to['anpa_take_key'] = '{}={}'.format(take_key, sequence)
        if target.get(ITEM_STATE) in PUBLISH_STATES:
            to['anpa_take_key'] = '{} (reopens)'.format(take_key)
        to[config.VERSION] = 1
        to[ITEM_STATE] = CONTENT_STATE.PROGRESS if to.get('task', {}).get('desk', None) else CONTENT_STATE.DRAFT

        copy_from = package if (package.get(ITEM_STATE) in PUBLISH_STATES) else target
        for field in self.fields_for_creating_take:
            to[field] = copy_from.get(field)

    def package_story_as_a_take(self, target, takes_package, link):
        """
        This function create the takes package using the target item metadata and links the
        target and link together in the takes package as target as take1 and link as take2.
        If the link is not provided then only target is added to the takes package.
        :param dict target: Target item to be added to the takes package.
        :param dict takes_package: takes package.
        :param dict link: item to be linked.
        :return: Takes Package Id
        """
        takes_package[ITEM_TYPE] = CONTENT_TYPE.COMPOSITE
        takes_package[PACKAGE_TYPE] = TAKES_PACKAGE
        fields_for_creating_takes_package = self.fields_for_creating_take.copy()
        fields_for_creating_takes_package.extend(['publish_schedule', 'event_id', 'rewrite_of', 'task',
                                                  EMBARGO])

        for field in fields_for_creating_takes_package:
            if field in target:
                takes_package[field] = target.get(field)

        takes_package.setdefault(config.VERSION, 1)

        create_root_group([takes_package])
        self.__link_items__(takes_package, target, link)

        ids = get_resource_service(ARCHIVE).post([takes_package])
        insert_into_versions(id_=ids[0])
        original_target = get_resource_service(ARCHIVE).find_one(req=None, _id=target['_id'])
        target[LINKED_IN_PACKAGES] = original_target[LINKED_IN_PACKAGES]

        return ids[0]

    def link_as_next_take(self, target, link):
        """
        Check if target has an associated takes package. If not, create it and add target as a take.
        Check if the target is the last take, if not, resolve the last take. Copy metadata from the target and add it
        as the next take and return the update link item

        :return: the updated link item
        """

        takes_package_id = self.get_take_package_id(target)
        archive_service = get_resource_service(ARCHIVE)
        takes_package = archive_service.find_one(req=None, _id=takes_package_id) if takes_package_id else {}

        if not takes_package:
            # setting the sequence to 1 for target.
            updates = {SEQUENCE: 1}
            resolve_document_version(updates, ARCHIVE, 'PATCH', target)
            archive_service.patch(target.get(config.ID_FIELD), updates)

        if not link.get(config.ID_FIELD):
            self.__copy_metadata__(target, link, takes_package)
            archive_service.post([link])

        if not takes_package_id:
            takes_package_id = self.package_story_as_a_take(target, takes_package, link)
        else:
            self.__link_items__(takes_package, target, link)
            del takes_package[config.ID_FIELD]
            resolve_document_version(takes_package, ARCHIVE, 'PATCH', takes_package)
            archive_service.patch(takes_package_id, takes_package)

        if link.get(SEQUENCE):
            archive_service.patch(link[config.ID_FIELD], {SEQUENCE: link[SEQUENCE]})

        insert_into_versions(id_=takes_package_id)

        return link

    def is_last_takes_package_item(self, doc):
        """
        checks whether if the item is the last item of the takes package.
        if the item is not the last item then raise exception
        :param dict doc: take of a package
        """
        takes_package = self.get_take_package(doc)
        if takes_package:
            if LAST_TAKE not in takes_package:
                return True
            return takes_package[LAST_TAKE] == doc[config.ID_FIELD]

        return True

    def process_killed_takes_package(self, doc):
        """
        If the takes packages is killed then spike the unpublished item
        :param dict doc: killed item
        """
        takes_package = self.get_take_package(doc)

        if takes_package:
            spike_service = get_resource_service('archive_spike')
            groups = takes_package.get('groups', [])
            if groups:
                refs = next(group.get('refs') for group in groups if group['id'] == MAIN_GROUP)
                for sequence in range(takes_package.get(SEQUENCE, 0), 0, -1):
                    try:
                        ref = next(ref for ref in refs if ref.get(SEQUENCE) == sequence)
                        updates = {ITEM_STATE: CONTENT_STATE.SPIKED}
                        spike_service.patch(ref[RESIDREF], updates)
                    except InvalidStateTransitionError:
                        # for published items it will InvalidStateTransitionError
                        break
                    except SuperdeskApiError:
                        # if not the last take
                        break
                    except:
                        logger.exception("Unexpected error while spiking items of takes package")
                        break

    def get_first_take_in_takes_package(self, item):
        """
        Returns the id of the first take in the takes package.
        :param dict item: document
        :return str: id of the first take else None
        """
        package = self.get_take_package(item)
        if package:
            refs = self._get_package_refs(package)
            if refs:
                ref = next((ref for ref in refs if ref.get(SEQUENCE) == 1
                            and ref.get(RESIDREF, '') != item.get(config.ID_FIELD, '')), None)
                if ref:
                    return ref.get(RESIDREF, None)

        return None

    def _get_package_refs(self, package):
        """
        Get refs from the takes package
        :param dict package: takes package
        :return: return refs from the takes package. If not takes package or no refs found then None
        """
        refs = None
        if package:
            groups = package.get('groups', [])
            refs = next((group.get('refs') for group in groups if group['id'] == MAIN_GROUP), None)

        return refs

    def can_publish_take(self, package, sequence):
        """
        Takes can be published only in ascending order. This function check that if there are any
        unpublished takes before the current take.
        :param dict package: takes packages
        :param int sequence: take sequence of the published take
        :return: True if takes are published in correct order else false.
        """
        refs = self._get_package_refs(package)
        if refs:
            takes = [ref.get(RESIDREF) for ref in refs if ref.get(SEQUENCE) < sequence]
            # elastic filter for the archive resource filters out the published items
            archive_service = get_resource_service(ARCHIVE)
            query = {'query': {'filtered': {'filter': {'terms': {'_id': takes}}}}}
            request = ParsedRequest()
            request.args = {'source': json.dumps(query)}
            items = archive_service.get(req=request, lookup=None)
            return items.count() == 0

        return True

    def get_published_takes(self, takes_package):
        """
        Get all the published takes in the takes packages.
        :param takes_package: takes package
        :return: List of publishes takes.
        """
        refs = self._get_package_refs(takes_package)
        if not refs:
            return []

        takes = [ref.get(RESIDREF) for ref in refs]

        query = {'$and':
                 [
                     {config.ID_FIELD: {'$in': takes}},
                     {ITEM_STATE: {'$in': [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED]}}
                 ]}
        request = ParsedRequest()
        request.sort = SEQUENCE
        return list(get_resource_service(ARCHIVE).get_from_mongo(req=request, lookup=query))
