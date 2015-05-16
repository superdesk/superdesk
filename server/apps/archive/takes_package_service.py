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
from eve.utils import config
from superdesk.errors import SuperdeskApiError
from superdesk import get_resource_service
from apps.archive.archive import SOURCE as ARCHIVE
from apps.content import LINKED_IN_PACKAGES, PACKAGE_TYPE, TAKES_PACKAGE, ITEM_TYPE, ITEM_TYPE_COMPOSITE, PACKAGE
from .common import ASSOCIATIONS, MAIN_GROUP, SEQUENCE, PUBLISH_STATES
from .archive_composite import get_item_ref, create_root_group

logger = logging.getLogger(__name__)


class TakesPackageService():

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

    def __strip_take_info__(self, take_info):
        take_index = take_info.rfind('=')
        return take_info[0:take_index] if take_info[take_index + 1:].isdigit() else take_info

    def __copy_metadata__(self, target, to, package):
        # TODO: length validation may be required.
        # if target is the first take hence default sequence is for first take.
        sequence = package.get(SEQUENCE, 1) if package else 1
        sequence = self.__next_sequence__(sequence)
        headline = self.__strip_take_info__(target.get('headline', ''))
        take_key = self.__strip_take_info__(target.get('anpa_take_key', ''))
        to['headline'] = '{}={}'.format(headline, sequence)
        to['anpa_take_key'] = '{}={}'.format(take_key, sequence)
        to['_version'] = 1
        to[config.CONTENT_STATE] = 'in_progress' if to.get('task', {}).get('desk', None) else 'draft'

        copy_from = package if (package.get(config.CONTENT_STATE) in PUBLISH_STATES) else target
        for field in ['abstract', 'anpa-category', 'pubstatus', 'destination_groups',
                      'slugline', 'urgency', 'subject', 'dateline']:
            to[field] = copy_from.get(field)

    def create_takes_package(self, takes_package, target, link):
        takes_package.update({
            ITEM_TYPE: ITEM_TYPE_COMPOSITE,
            PACKAGE_TYPE: TAKES_PACKAGE,
            'headline': target.get('headline'),
            'slugline': target.get('slugline'),
            'abstract': target.get('abstract')
        })
        create_root_group([takes_package])
        self.__link_items__(takes_package, target, link)
        archive_service = get_resource_service(ARCHIVE)
        tasks_service = get_resource_service('tasks')
        ids = archive_service.post([takes_package])
        takes_package_id = ids[0]

        # send the package to the desk where the first take was sent
        current_task = target.get('task')
        tasks_service.patch(takes_package_id, {'task': current_task})

    def link_as_next_take(self, target, link):
        """
        # check if target has an associated takes package
        # if not, create it and add target as a take
        # check if the target is the last take, if not, resolve the last take
        # copy metadata from the target and add it as the next take
        # return the update link item
        """
        takes_package_id = self.get_take_package_id(target)
        archive_service = get_resource_service(ARCHIVE)
        takes_package = archive_service.find_one(req=None, _id=takes_package_id) if takes_package_id else {}

        if not link.get('_id'):
            self.__copy_metadata__(target, link, takes_package)
            archive_service.post([link])

        if not takes_package_id:
            self.create_takes_package(takes_package, target, link)
        else:
            self.__link_items__(takes_package, target, link)
            del takes_package['_id']
            archive_service.patch(takes_package_id, takes_package)

        return link
